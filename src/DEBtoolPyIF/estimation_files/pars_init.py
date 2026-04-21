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
        InitializeParametersSection(parameter_registry=resolved_registry),
        ParsInitAddChemSection(include_addchem=include_addchem),
        ParsInitPackingSection(),
    )


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
        final_sections = (
            build_registry_pars_init_sections(
                parameter_registry=parameter_registry,
                model=model,
                include_addchem=include_addchem,
            )
            if sections is None
            else tuple(sections)
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
        return self.default_sections()


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
        final_sections = (
            build_registry_pars_init_sections(
                parameter_registry=parameter_registry,
                model=model,
                include_addchem=include_addchem,
            )
            if sections is None
            else tuple(sections)
        )
        super().__init__(source=source, sections=final_sections)
