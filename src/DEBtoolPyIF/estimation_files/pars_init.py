"""pars_init.m template families and shared section helpers."""

from __future__ import annotations

from pathlib import Path

from .templates import EstimationFileSection, ProgrammaticTemplate, StaticSection, SubstitutionTemplate
from ..parameters import ParameterDefinition, ParameterRegistry, build_default_parameter_registry
from ..utils.data_conversion import convert_numeric_array_to_matlab, convert_string_to_matlab


SUPPLEMENTAL_PARAMETER_ORDER = ("T_A", "z", "F_m", "kap_R", "p_T", "k_J", "s_G", "f")
PARS_INIT_SLOT_NAMES = (
    "function_header",
    "model_metadata",
    "base_parameters",
    "addchem",
    "packing",
)
PARS_INIT_BASE_REQUIRED_KEYS = (
    "function_header",
    "model_metadata",
    "base_parameters",
    "addchem",
    "packing",
)


class ParsInitFunctionHeaderSection(EstimationFileSection):
    slot_name = "function_header"

    def render(self, context) -> str:
        return f"function [par, metaPar, txtPar] = pars_init_{context.species_name}(metaData)"


class ParsInitModelMetadataSection(EstimationFileSection):
    slot_name = "model_metadata"

    def __init__(self, model: str = "stx") -> None:
        self.model = model

    def render(self, _context) -> str:
        return "\n".join(
            [
                "metaPar.model = {model};".format(model=convert_string_to_matlab(self.model)),
                "",
                "%% reference parameter and model parameters",
            ]
        )


class ParsInitBaseParametersSection(EstimationFileSection):
    slot_name = "base_parameters"

    def __init__(
        self,
        *,
        parameter_registry: ParameterRegistry | None = None,
        custom_parameters: tuple[ParameterDefinition, ...] = (),
    ) -> None:
        self.parameter_registry = (
            build_default_parameter_registry() if parameter_registry is None else parameter_registry
        )
        self.custom_parameters = custom_parameters

    def _registry(self) -> ParameterRegistry:
        return self.parameter_registry.merged(list(self.custom_parameters))

    def render(self, context) -> str:
        registry = self._registry()
        full_pars = context.full_pars_dict
        parameter_order = []
        for parameter_name in ("T_ref", *full_pars.keys(), *SUPPLEMENTAL_PARAMETER_ORDER):
            if parameter_name not in parameter_order:
                parameter_order.append(parameter_name)

        lines = []
        for parameter_name in parameter_order:
            definition = registry.get(parameter_name)
            if definition is None:
                raise ValueError(
                    f"No parameter definition available for '{parameter_name}'. "
                    "Provide a CustomParameterDefinition when generating pars_init.m."
                )

            if parameter_name in full_pars:
                value = full_pars[parameter_name]
            else:
                if definition.default_value is None:
                    continue
                value = definition.default_value

            free_value = 1 if parameter_name in context.tier_pars else definition.default_free
            lines.append(
                "par.{name} = {value}; free.{name} = {free}; units.{name} = {units}; "
                "label.{name} = {label};".format(
                    name=parameter_name,
                    value=convert_numeric_array_to_matlab(value, format_codes=definition.float_format),
                    free=free_value,
                    units=convert_string_to_matlab(definition.units),
                    label=convert_string_to_matlab(definition.label),
                )
            )
        return "\n".join(lines)


class ParsInitAddChemSection(EstimationFileSection):
    slot_name = "addchem"

    def __init__(self, include_addchem: bool = True) -> None:
        self.include_addchem = include_addchem

    def render(self, _context) -> str:
        if not self.include_addchem:
            return ""
        return "\n".join(
            [
                "%% set chemical parameters from Kooy2010",
                "[par, units, label, free] = addchem(par, units, label, free, metaData.phylum, metaData.class);",
            ]
        )


class ParsInitPackingSection(StaticSection):
    def __init__(self):
        super().__init__(
            slot_name="packing",
            content="""%% Pack output
txtPar.units = units;
txtPar.label = label;
par.free = free;

end""",
        )


def build_pars_init_substitutions(
    context,
    sections: tuple[EstimationFileSection, ...],
    *,
    allowed_keys: tuple[str, ...] = PARS_INIT_SLOT_NAMES,
) -> dict[str, str]:
    rendered_keys = {key: "" for key in allowed_keys}
    for section in sections:
        section.validate(allowed_keys)
        rendered_keys[section.slot_name] += section.render(context).rstrip() + "\n\n"
    return {key: value.rstrip() for key, value in rendered_keys.items()}


class ParsInitTemplate:
    """Shared file-family behavior for pars_init template classes."""

    template_label = "pars_init"
    allowed_section_keys = PARS_INIT_SLOT_NAMES
    required_section_keys = PARS_INIT_BASE_REQUIRED_KEYS

    def __init__(
        self,
        *,
        parameter_registry: ParameterRegistry | None = None,
        custom_parameters: tuple[ParameterDefinition, ...] = (),
        model: str = "stx",
        include_addchem: bool = True,
    ) -> None:
        self.parameter_registry = (
            build_default_parameter_registry() if parameter_registry is None else parameter_registry
        )
        self.custom_parameters = custom_parameters
        self.model = model
        self.include_addchem = include_addchem

    @classmethod
    def base_required_sections(
        cls,
        *,
        parameter_registry: ParameterRegistry,
        custom_parameters: tuple[ParameterDefinition, ...],
        model: str,
        include_addchem: bool,
    ) -> tuple[EstimationFileSection, ...]:
        return (
            ParsInitFunctionHeaderSection(),
            ParsInitModelMetadataSection(model=model),
            ParsInitBaseParametersSection(
                parameter_registry=parameter_registry,
                custom_parameters=custom_parameters,
            ),
            ParsInitAddChemSection(include_addchem=include_addchem),
            ParsInitPackingSection(),
        )

    @classmethod
    def required_sections(
        cls,
        *,
        parameter_registry: ParameterRegistry | None = None,
        custom_parameters: tuple[ParameterDefinition, ...] = (),
        model: str = "stx",
        include_addchem: bool = True,
    ) -> tuple[EstimationFileSection, ...]:
        resolved_registry = (
            build_default_parameter_registry() if parameter_registry is None else parameter_registry
        )
        return cls.base_required_sections(
            parameter_registry=resolved_registry,
            custom_parameters=custom_parameters,
            model=model,
            include_addchem=include_addchem,
        )

    @classmethod
    def default_sections(
        cls,
        *,
        parameter_registry: ParameterRegistry | None = None,
        custom_parameters: tuple[ParameterDefinition, ...] = (),
        model: str = "stx",
        include_addchem: bool = True,
    ) -> tuple[EstimationFileSection, ...]:
        return cls.required_sections(
            parameter_registry=parameter_registry,
            custom_parameters=custom_parameters,
            model=model,
            include_addchem=include_addchem,
        )

    def get_section_key(self, section) -> str:
        return section.slot_name

    def render_section(self, section, context) -> str:
        return section.render(context)


class ParsInitProgrammaticTemplate(ParsInitTemplate, ProgrammaticTemplate):
    """Validated direct-assembly programmatic pars_init template."""

    def __init__(
        self,
        *,
        parameter_registry: ParameterRegistry | None = None,
        custom_parameters: tuple[ParameterDefinition, ...] = (),
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


class ParsInitSubstitutionTemplate(ParsInitTemplate, SubstitutionTemplate):
    """Source-backed pars_init template with construction-time section matching."""

    def __init__(
        self,
        *,
        source: str | Path,
        parameter_registry: ParameterRegistry | None = None,
        custom_parameters: tuple[ParameterDefinition, ...] = (),
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
        SubstitutionTemplate.__init__(
            self,
            source=source,
            sections=sections,
            template_label=self.template_label,
        )

    def get_default_sections(self) -> tuple:
        return self.default_sections(
            parameter_registry=self.parameter_registry,
            custom_parameters=self.custom_parameters,
            model=self.model,
            include_addchem=self.include_addchem,
        )
