"""Generic pars_init.m section implementations."""

from __future__ import annotations

from .pars_init_base import ParsInitSection
from ..parameters import ParameterRegistry
from ..utils.data_conversion import convert_numeric_array_to_matlab, convert_string_to_matlab


SUPPLEMENTAL_PARAMETER_ORDER = ("T_A", "z", "F_m", "kap_R", "p_T", "k_J", "s_G", "f")


class ParsInitFunctionHeader(ParsInitSection):
    key = "function_header"
    template_families = ("pars_init",)
    section_tags = ("header",)
    matlab_code = "function [par, metaPar, txtPar] = pars_init_${species_name}(metaData)"

    def __init__(self, *, species_name: str | None = None) -> None:
        self.species_name = species_name
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        if self.species_name is None:
            return {}
        return {"species_name": self.species_name}

    def get_render_substitutions(self, context) -> dict[str, str]:
        if self.species_name is not None:
            return {}
        return {"species_name": context.species_name}


class AddModelMedatadaSection(ParsInitSection):
    key = "model_metadata"
    template_families = ("pars_init",)
    section_tags = ("metadata",)
    matlab_code = """metaPar.model = ${model};

%% reference parameter and model parameters"""

    def __init__(self, model: str = "nat") -> None:
        self.model = model
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        return {"model": convert_string_to_matlab(self.model)}


class InitializeParametersSection(ParsInitSection):
    key = "base_parameters"
    template_families = ("pars_init",)
    section_tags = ("parameters",)

    def __init__(
        self,
        *,
        parameter_registry: ParameterRegistry | None = None,
    ) -> None:
        self.parameter_registry = ParameterRegistry.default() if parameter_registry is None else parameter_registry

    def render(self, context) -> str:
        registry = self.parameter_registry
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
                    "Provide a ParameterRegistry that includes this definition when generating pars_init.m."
                )

            if parameter_name in full_pars:
                value = full_pars[parameter_name]
            else:
                if definition.default_value is None:
                    continue
                value = definition.default_value
            # TODO: This currently depends on context.tier_pars which is multitier specific. Need to refactor
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


class ParsInitAddChemSection(ParsInitSection):
    key = "addchem"
    template_families = ("pars_init",)
    section_tags = ("chemistry",)
    matlab_code = """%% set chemical parameters from Kooy2010
[par, units, label, free] = addchem(par, units, label, free, metaData.phylum, metaData.class);"""

    def __init__(self, include_addchem: bool = True) -> None:
        self.include_addchem = include_addchem
        super().__init__()

    def render(self, context) -> str:
        if not self.include_addchem:
            return ""
        return super().render(context)


class ParsInitPackingSection(ParsInitSection):
    key = "packing"
    template_families = ("pars_init",)
    section_tags = ("packing",)
    matlab_code = """%% Pack output
txtPar.units = units;
txtPar.label = label;
par.free = free;

end"""
