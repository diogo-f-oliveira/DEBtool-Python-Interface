"""Multitier-specific pars_init template families."""

from __future__ import annotations

from pathlib import Path

from ..estimation_files.pars_init import (
    ParsInitSubstitutionTemplate,
    ParsInitTemplate,
    build_registry_pars_init_sections,
)
from ..estimation_files.pars_init_base import ParsInitSection
from ..estimation_files.templates import ProgrammaticTemplate
from ..parameters import ParameterRegistry


class MultitierParsInitLoopsSection(ParsInitSection):
    key = "tier_parameter_loops"
    template_families = ("multitier_pars_init",)
    section_tags = ("tier_parameters",)
    matlab_code = """%% Set tier parameters
for e = 1:length(metaData.entity_list)
    entity_id = metaData.entity_list{e};
    for p = 1:length(metaData.tier_pars)
        par_name = metaData.tier_pars{p};
        varname = [par_name '_' entity_id];

        par.(varname) = metaData.tier_par_init_values.(par_name).(entity_id);
        free.(varname) = 1;
        units.(varname) = units.(par_name);
        label.(varname) = [label.(par_name) '${tier_label_template}' entity_id];
    end
end"""

    def __init__(self, tier_label_template: str = " for tier entity "):
        self.tier_label_template = tier_label_template
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        return {"tier_label_template": self.tier_label_template}


class MultitierParsInitTemplate(ParsInitTemplate):
    """Shared file-family behavior for multitier pars_init template classes."""

    template_families = ("pars_init", "multitier_pars_init")

    @classmethod
    def required_sections(cls) -> tuple[ParsInitSection, ...]:
        base_sections = list(super().required_sections())
        base_sections.insert(-1 if base_sections else 0, MultitierParsInitLoopsSection())
        return tuple(base_sections)

    @classmethod
    def default_sections(cls) -> tuple[ParsInitSection, ...]:
        return cls.required_sections()


class MultitierParsInitProgrammaticTemplate(MultitierParsInitTemplate, ProgrammaticTemplate):
    """Validated direct-assembly programmatic multitier pars_init template."""

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


class RegistryMultitierParsInitProgrammaticTemplate(MultitierParsInitProgrammaticTemplate):
    """Programmatic multitier pars_init template backed by a parameter registry."""

    def __init__(
        self,
        *,
        parameter_registry: ParameterRegistry | None = None,
        model: str = "nat",
        include_addchem: bool = True,
        sections: tuple[ParsInitSection, ...] | None = None,
    ) -> None:
        final_sections = (
            build_registry_multitier_pars_init_sections(
                parameter_registry=parameter_registry,
                model=model,
                include_addchem=include_addchem,
            )
            if sections is None
            else tuple(sections)
        )
        super().__init__(sections=final_sections)


class MultitierParsInitSubstitutionTemplate(MultitierParsInitTemplate, ParsInitSubstitutionTemplate):
    """Source-backed multitier pars_init template with construction-time section matching."""

    def __init__(
        self,
        *,
        source: str | Path,
        sections: tuple[ParsInitSection, ...] | None = None,
    ) -> None:
        ParsInitSubstitutionTemplate.__init__(
            self,
            source=source,
            sections=sections,
        )


def build_registry_multitier_pars_init_sections(
    *,
    parameter_registry: ParameterRegistry | None = None,
    model: str = "nat",
    include_addchem: bool = True,
) -> tuple[ParsInitSection, ...]:
    sections = list(
        build_registry_pars_init_sections(
            parameter_registry=parameter_registry,
            model=model,
            include_addchem=include_addchem,
        )
    )
    sections.insert(-1 if sections else 0, MultitierParsInitLoopsSection())
    return tuple(sections)


class RegistryMultitierParsInitSubstitutionTemplate(MultitierParsInitSubstitutionTemplate):
    """Source-backed multitier pars_init template backed by a parameter registry."""

    def __init__(
        self,
        *,
        source: str | Path,
        parameter_registry: ParameterRegistry | None = None,
        model: str = "nat",
        include_addchem: bool = True,
        sections: tuple[ParsInitSection, ...] | None = None,
    ) -> None:
        final_sections = (
            build_registry_multitier_pars_init_sections(
                parameter_registry=parameter_registry,
                model=model,
                include_addchem=include_addchem,
            )
            if sections is None
            else tuple(sections)
        )
        super().__init__(source=source, sections=final_sections)
