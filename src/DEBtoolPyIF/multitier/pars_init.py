"""Multitier-specific pars_init template families."""

from __future__ import annotations

from pathlib import Path

from ..estimation_files.pars_init import (
    PARS_INIT_BASE_REQUIRED_KEYS,
    PARS_INIT_SLOT_NAMES,
    ParsInitProgrammaticTemplate,
    ParsInitSubstitutionTemplate,
    ParsInitTemplate,
)
from ..estimation_files.templates import EstimationFileSection, ProgrammaticTemplate


MULTITIER_PARS_INIT_SLOT_NAMES = PARS_INIT_SLOT_NAMES + ("tier_parameter_loops",)
MULTITIER_PARS_INIT_REQUIRED_KEYS = PARS_INIT_BASE_REQUIRED_KEYS + ("tier_parameter_loops",)


class MultitierParsInitLoopsSection(EstimationFileSection):
    slot_name = "tier_parameter_loops"

    def __init__(self, tier_label_template: str = " for tier entity "):
        self.tier_label_template = tier_label_template

    def render(self, context) -> str:
        return "\n".join(
            [
                "%% Set tier parameters",
                "for e = 1:length(metaData.entity_list)",
                "    entity_id = metaData.entity_list{e};",
                "    for p = 1:length(metaData.tier_pars)",
                "        par_name = metaData.tier_pars{p};",
                "        varname = [par_name '_' entity_id];",
                "",
                "        par.(varname) = metaData.tier_par_init_values.(par_name).(entity_id);",
                "        free.(varname) = 1;",
                "        units.(varname) = units.(par_name);",
                "        label.(varname) = [label.(par_name) '"
                + self.tier_label_template
                + "' entity_id];",
                "    end",
                "end",
            ]
        )


class MultitierParsInitTemplate(ParsInitTemplate):
    """Shared file-family behavior for multitier pars_init template classes."""

    allowed_section_keys = MULTITIER_PARS_INIT_SLOT_NAMES
    required_section_keys = MULTITIER_PARS_INIT_REQUIRED_KEYS

    @classmethod
    def required_sections(
        cls,
        *,
        parameter_registry=None,
        custom_parameters=(),
        model: str = "stx",
        include_addchem: bool = True,
    ) -> tuple[EstimationFileSection, ...]:
        base_sections = list(
            super().required_sections(
                parameter_registry=parameter_registry,
                custom_parameters=custom_parameters,
                model=model,
                include_addchem=include_addchem,
            )
        )
        base_sections.insert(-1 if base_sections else 0, MultitierParsInitLoopsSection())
        return tuple(base_sections)

    @classmethod
    def default_sections(
        cls,
        *,
        parameter_registry=None,
        custom_parameters=(),
        model: str = "stx",
        include_addchem: bool = True,
    ) -> tuple[EstimationFileSection, ...]:
        return cls.required_sections(
            parameter_registry=parameter_registry,
            custom_parameters=custom_parameters,
            model=model,
            include_addchem=include_addchem,
        )


class MultitierParsInitProgrammaticTemplate(MultitierParsInitTemplate, ProgrammaticTemplate):
    """Validated direct-assembly programmatic multitier pars_init template."""

    def __init__(
        self,
        *,
        parameter_registry=None,
        custom_parameters=(),
        model: str = "stx",
        include_addchem: bool = True,
        sections: tuple[EstimationFileSection, ...] | None = None,
    ) -> None:
        ParsInitTemplate.__init__(
            self,
            parameter_registry=parameter_registry,
            custom_parameters=custom_parameters,
            model=model,
            include_addchem=include_addchem,
        )
        final_sections = self.required_sections(
            parameter_registry=self.parameter_registry,
            custom_parameters=self.custom_parameters,
            model=self.model,
            include_addchem=self.include_addchem,
        ) if sections is None else tuple(sections)
        ProgrammaticTemplate.__init__(
            self,
            sections=final_sections,
            allowed_section_keys=self.allowed_section_keys,
            required_section_keys=self.required_section_keys,
            template_label=self.template_label,
        )


class MultitierParsInitSubstitutionTemplate(MultitierParsInitTemplate, ParsInitSubstitutionTemplate):
    """Source-backed multitier pars_init template with construction-time section matching."""

    def __init__(
        self,
        *,
        source: str | Path,
        parameter_registry=None,
        custom_parameters=(),
        model: str = "stx",
        include_addchem: bool = True,
        sections: tuple[EstimationFileSection, ...] | None = None,
    ) -> None:
        ParsInitSubstitutionTemplate.__init__(
            self,
            source=source,
            parameter_registry=parameter_registry,
            custom_parameters=custom_parameters,
            model=model,
            include_addchem=include_addchem,
            sections=sections,
        )
