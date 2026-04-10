"""Shared template bases and helpers for estimation-file generation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from string import Template


class EstimationFileTemplate(ABC):
    """Base class for all estimation-file template strategies."""

    @abstractmethod
    def validate(self, context) -> None:
        """Validate that the template can render for the provided context."""

    @abstractmethod
    def render(self, context) -> str:
        """Render the final estimation file."""


class MatlabSnippetMixin:
    """Shared snippet-backed rendering behavior for section classes."""

    matlab_code: str = ""

    def __init__(self, *, matlab_code: str | None = None) -> None:
        source = self.matlab_code if matlab_code is None else matlab_code
        self._bound_matlab_code = render_source_template(
            source,
            substitutions=self.get_init_substitutions(),
        )
        referenced_keys = extract_template_keys(self._bound_matlab_code, "section")
        self._bound_template = Template(self._bound_matlab_code) if referenced_keys else None

    def get_init_substitutions(self) -> dict[str, str]:
        return {}

    def get_render_substitutions(self, *args, **kwargs) -> dict[str, str]:
        return {}

    def get_matlab_code(self) -> str:
        return self._bound_matlab_code

    def _render_matlab_code(self, *args, **kwargs) -> str:
        if self._bound_template is None:
            return self._bound_matlab_code
        return self._bound_template.safe_substitute(self.get_render_substitutions(*args, **kwargs))


class EstimationFileSection(MatlabSnippetMixin, ABC):
    """Render one named slot inside a sectioned estimation-file template."""

    slot_name: str

    def __init__(self, *, matlab_code: str | None = None) -> None:
        super().__init__(matlab_code=matlab_code)

    def validate(self, allowed_slots: tuple[str, ...]) -> None:
        if self.slot_name not in allowed_slots:
            raise ValueError(
                f"Unsupported slot '{self.slot_name}' for this estimation file. "
                f"Expected one of: {', '.join(allowed_slots)}."
            )

    def render(self, context) -> str:
        return self._render_matlab_code(context)


@dataclass(frozen=True)
class CopyFileTemplate(EstimationFileTemplate):
    """A file copied verbatim from an existing filesystem path."""

    path: str | Path

    def get_source(self) -> str:
        return Path(self.path).read_text(encoding="utf-8")

    def validate(self, _context) -> None:
        return None

    def render(self, _context) -> str:
        return self.get_source()


def extract_template_keys(source: str, template_label: str) -> tuple[str, ...]:
    keys = []
    for match in Template.pattern.finditer(source):
        named = match.group("named") or match.group("braced")
        invalid = match.group("invalid")
        if invalid is not None:
            raise ValueError(f"Invalid {template_label} template placeholder syntax near '${invalid}'.")
        if named:
            keys.append(named)
    return tuple(dict.fromkeys(keys))


def render_source_template(
    source: str,
    *,
    substitutions: dict[str, str],
) -> str:
    return Template(source).safe_substitute(substitutions)


class ProgrammaticTemplate(EstimationFileTemplate, ABC):
    """Validated base class for fully programmatic section-assembled estimation files."""

    template_label = "estimation file"

    def __init__(
        self,
        *,
        sections: tuple = (),
        allowed_section_keys: tuple[str, ...],
        required_section_keys: tuple[str, ...],
        template_label: str | None = None,
    ) -> None:
        self._programmatic_sections = tuple(sections)
        self._programmatic_allowed_section_keys = tuple(allowed_section_keys)
        self._programmatic_required_section_keys = tuple(required_section_keys)
        if template_label is not None:
            self.template_label = template_label
        self._validate_static_contract()

    def get_sections(self) -> tuple:
        return self._programmatic_sections

    @abstractmethod
    def get_section_key(self, section) -> str:
        raise NotImplementedError

    @abstractmethod
    def render_section(self, section, context) -> str:
        raise NotImplementedError

    def validate_context(self, _context) -> None:
        return None

    def _validate_sections(
        self,
        *,
        sections: tuple,
        allowed_keys: tuple[str, ...],
        required_section_keys: tuple[str, ...],
    ) -> tuple:
        seen_keys: set[str] = set()

        for section in sections:
            validator = getattr(section, "validate", None)
            if callable(validator):
                validator(allowed_keys)

            key = self.get_section_key(section)
            if key in seen_keys:
                raise ValueError(
                    f"Duplicate {self.template_label} section key '{key}'. "
                    "Use one section per required block."
                )
            seen_keys.add(key)

        missing_required = [key for key in required_section_keys if key not in seen_keys]
        if missing_required:
            raise ValueError(
                f"Missing required {self.template_label} sections: "
                + ", ".join(missing_required)
                + "."
            )
        return sections

    def _validate_static_contract(self) -> None:
        self._validate_sections(
            sections=self.get_sections(),
            allowed_keys=self._programmatic_allowed_section_keys,
            required_section_keys=self._programmatic_required_section_keys,
        )

    def _render_sections(self, context, sections: tuple | None = None) -> str:
        sections = self.get_sections() if sections is None else sections
        rendered_sections: list[str] = []
        for section in sections:
            output = self.render_section(section, context).rstrip()
            if output:
                rendered_sections.append(output)
        return "\n\n".join(rendered_sections)

    def validate(self, context) -> None:
        self.validate_context(context)

    def render(self, context) -> str:
        self.validate(context)
        return self._render_sections(context)


class SubstitutionTemplate(EstimationFileTemplate, ABC):
    """Source-backed template that matches placeholders to sections at construction."""

    template_label = "estimation file"

    def __init__(
        self,
        *,
        source: str | Path,
        sections: tuple | None = None,
        template_label: str | None = None,
    ) -> None:
        if template_label is not None:
            self.template_label = template_label
        self._source = self._read_source(source)
        self._referenced_keys = extract_template_keys(self._source, self.template_label)
        candidate_sections = self.get_default_sections() if sections is None else tuple(sections)
        self._matched_sections = self._match_sections(candidate_sections, self._referenced_keys)

    def _read_source(self, source: str | Path) -> str:
        if isinstance(source, Path):
            return source.read_text(encoding="utf-8")
        return source

    @abstractmethod
    def get_default_sections(self) -> tuple:
        raise NotImplementedError

    @abstractmethod
    def get_section_key(self, section) -> str:
        raise NotImplementedError

    @abstractmethod
    def render_section(self, section, context) -> str:
        raise NotImplementedError

    def get_source(self) -> str:
        return self._source

    def get_sections(self) -> tuple:
        return self._matched_sections

    def get_referenced_keys(self) -> tuple[str, ...]:
        return self._referenced_keys

    def validate(self, _context) -> None:
        return None

    def _match_sections(self, sections: tuple, referenced_keys: tuple[str, ...]) -> tuple:
        section_by_key = {}
        for section in sections:
            key = self.get_section_key(section)
            section_by_key[key] = section
        return tuple(section_by_key[key] for key in referenced_keys if key in section_by_key)

    def build_substitutions(self, context) -> dict[str, str]:
        substitutions = {}
        for section in self.get_sections():
            substitutions[self.get_section_key(section)] = self.render_section(section, context)
        return substitutions

    def render(self, context) -> str:
        return render_source_template(
            self.get_source(),
            substitutions=self.build_substitutions(context),
        )
