"""Pseudo-data sections for mydata.m generation."""

from __future__ import annotations

from ..parameters import ParameterDefinition
from ..utils.data_conversion import convert_numeric_array_to_matlab, convert_string_to_matlab
from .mydata_base import MyDataSection


class AddPseudoDataSection(MyDataSection):
    key = "add_pseudodata_block"
    template_families = ("mydata",)
    section_tags = ("pseudodata",)
    matlab_code = """%% Add generic pseudo-data
[data, units, label, weights] = addpseudodata(data, units, label, weights);"""


class AddPseudoDataValue(MyDataSection):
    key = "additional_pseudodata_block"
    template_families = ("mydata",)
    section_tags = ("pseudodata",)

    def __init__(
        self,
        *,
        pseudo_data_values: (
            list[tuple[ParameterDefinition, int | float]]
            | tuple[tuple[ParameterDefinition, int | float], ...]
        ) = (),
    ) -> None:
        self.pseudo_data_values = tuple(pseudo_data_values)
        self._validate_entries()
        super().__init__()

    def _validate_entries(self) -> None:
        for entry in self.pseudo_data_values:
            if not isinstance(entry, tuple) or len(entry) != 2:
                raise TypeError(
                    "pseudo_data_values must contain (ParameterDefinition, value) pairs."
                )
            definition, _value = entry
            if not isinstance(definition, ParameterDefinition):
                raise TypeError(
                    "pseudo_data_values must contain ParameterDefinition instances as "
                    f"their first item, not {type(definition).__name__}."
                )

    def render(self, _context, _state) -> str:
        lines = []
        for definition, value in self.pseudo_data_values:
            rendered_value = convert_numeric_array_to_matlab(
                value,
                format_codes=definition.float_format,
            )
            lines.append(
                "data.psd.{name} = {value}; units.psd.{name} = {units}; "
                "label.psd.{name} = {label};".format(
                    name=definition.name,
                    value=rendered_value,
                    units=convert_string_to_matlab(definition.units),
                    label=convert_string_to_matlab(definition.label),
                )
            )
        return "\n".join(lines)
