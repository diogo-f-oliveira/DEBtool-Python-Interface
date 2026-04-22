"""pars_init.m template families and shared section helpers."""

from __future__ import annotations

from pathlib import Path

from .pars_init_base import ParsInitSection
from .pars_init_sections import (
    AddModelMedatadaSection,
    InitializeParametersSection,
    ParsInitAddChemSection,
    ParsInitFunctionHeader,
    ParsInitPackingSection,
    ParsInitReferenceTemperatureSection,
)
from .templates import ProgrammaticTemplate, SubstitutionTemplate
from ..parameters import ParameterRegistry, get_parameter_registry_of_typified_model


def build_registry_pars_init_sections(
    *,
    parameter_registry: ParameterRegistry | None = None,
    model: str = "std",
    include_addchem: bool = True,
) -> tuple[ParsInitSection, ...]:
    resolved_registry = (
        parameter_registry
        if parameter_registry is not None
        else get_parameter_registry_of_typified_model(model)
    )
    return (
        ParsInitFunctionHeader(),
        AddModelMedatadaSection(model=model),
        ParsInitReferenceTemperatureSection(),
        InitializeParametersSection(parameter_registry=resolved_registry),
        ParsInitAddChemSection(include_addchem=include_addchem),
        ParsInitPackingSection(),
    )


def _merge_registry_pars_init_sections(
    base_sections: tuple[ParsInitSection, ...],
    extra_sections: tuple[ParsInitSection, ...] | None = None,
) -> tuple[ParsInitSection, ...]:
    if extra_sections is None:
        return tuple(base_sections)

    base_sections = tuple(base_sections)
    extra_sections = tuple(extra_sections)
    base_keys = {section.key for section in base_sections}
    duplicate_keys: list[str] = []

    for section in extra_sections:
        if not isinstance(section, ParsInitSection):
            raise TypeError(
                "pars_init template sections must be ParsInitSection instances, "
                f"not {type(section).__name__}."
            )

        if section.key in base_keys and section.key not in duplicate_keys:
            duplicate_keys.append(section.key)

    if duplicate_keys:
        raise ValueError(
            "Registry-backed pars_init templates only accept extra sections with new keys. "
            "Duplicate built section keys are not allowed: "
            + ", ".join(duplicate_keys)
            + ". Use ParsInitProgrammaticTemplate, ParsInitSubstitutionTemplate, "
            "MultitierParsInitProgrammaticTemplate, or MultitierParsInitSubstitutionTemplate "
            "for full custom section replacement."
        )

    packing_index = next(
        index for index, section in reversed(tuple(enumerate(base_sections))) if section.key == "packing"
    )
    return base_sections[:packing_index] + extra_sections + base_sections[packing_index:]


class ParsInitTemplate:
    """Shared file-family behavior for pars_init template classes."""

    template_label = "pars_init"
    template_families = ("pars_init",)

    @classmethod
    def available_section_classes(cls) -> tuple[type[ParsInitSection], ...]:
        return ParsInitSection.registered_section_classes(
            template_families=cls.template_families,
        )

    @classmethod
    def allowed_section_keys(cls) -> tuple[str, ...]:
        registered_keys = tuple(dict.fromkeys(section_class.key for section_class in cls.available_section_classes()))
        required_keys = cls.required_section_keys()
        return required_keys + tuple(key for key in registered_keys if key not in required_keys)

    @classmethod
    def required_section_keys(cls) -> tuple[str, ...]:
        return tuple(section.key for section in cls.required_sections())

    @classmethod
    def section_classes_for_tag(cls, tag: str) -> tuple[type[ParsInitSection], ...]:
        return ParsInitSection.registered_section_classes(
            template_families=cls.template_families,
            tag=tag,
        )

    @classmethod
    def sections_for_tag(cls, tag: str) -> tuple[ParsInitSection, ...]:
        return tuple(section_class() for section_class in cls.section_classes_for_tag(tag))

    @classmethod
    def base_required_sections(
        cls,
    ) -> tuple[ParsInitSection, ...]:
        return (
            ParsInitFunctionHeader(),
            AddModelMedatadaSection(),
            ParsInitReferenceTemperatureSection(),
            InitializeParametersSection(),
            ParsInitAddChemSection(),
            ParsInitPackingSection(),
        )

    @classmethod
    def required_sections(cls) -> tuple[ParsInitSection, ...]:
        return cls.base_required_sections()

    @classmethod
    def default_sections(cls) -> tuple[ParsInitSection, ...]:
        return cls.required_sections()

    def get_section_key(self, section) -> str:
        if not isinstance(section, ParsInitSection):
            raise TypeError(
                "pars_init template sections must be ParsInitSection instances, "
                f"not {type(section).__name__}."
            )
        return section.key

    def render_section(self, section, context) -> str:
        return section.render(context)


class ParsInitProgrammaticTemplate(ParsInitTemplate, ProgrammaticTemplate):
    """Validated direct-assembly programmatic pars_init template."""

    def __init__(
        self,
        *,
        sections: tuple[ParsInitSection, ...] | None = None,
    ) -> None:
        final_sections = self.required_sections() if sections is None else tuple(sections)
        ProgrammaticTemplate.__init__(
            self,
            sections=final_sections,
            allowed_section_keys=self.allowed_section_keys(),
            required_section_keys=self.required_section_keys(),
            template_label=self.template_label,
        )


class RegistryParsInitProgrammaticTemplate(ParsInitProgrammaticTemplate):
    """Programmatic pars_init template backed by a parameter registry."""

    def __init__(
        self,
        *,
        parameter_registry: ParameterRegistry | None = None,
        model: str = "std",
        include_addchem: bool = True,
        sections: tuple[ParsInitSection, ...] | None = None,
    ) -> None:
        final_sections = _merge_registry_pars_init_sections(
            build_registry_pars_init_sections(
                parameter_registry=parameter_registry,
                model=model,
                include_addchem=include_addchem,
            ),
            sections,
        )
        super().__init__(sections=final_sections)


class ParsInitSubstitutionTemplate(ParsInitTemplate, SubstitutionTemplate):
    """Source-backed pars_init template with construction-time section matching."""

    def __init__(
        self,
        *,
        source: str | Path,
        sections: tuple[ParsInitSection, ...] | None = None,
    ) -> None:
        SubstitutionTemplate.__init__(
            self,
            source=source,
            sections=sections,
            template_label=self.template_label,
        )

    def get_default_sections(self) -> tuple:
        return build_registry_pars_init_sections()


class RegistryParsInitSubstitutionTemplate(ParsInitSubstitutionTemplate):
    """Source-backed pars_init template backed by a parameter registry."""

    def __init__(
        self,
        *,
        source: str | Path,
        parameter_registry: ParameterRegistry | None = None,
        model: str = "std",
        include_addchem: bool = True,
        sections: tuple[ParsInitSection, ...] | None = None,
    ) -> None:
        final_sections = _merge_registry_pars_init_sections(
            build_registry_pars_init_sections(
                parameter_registry=parameter_registry,
                model=model,
                include_addchem=include_addchem,
            ),
            sections,
        )
        super().__init__(source=source, sections=final_sections)
