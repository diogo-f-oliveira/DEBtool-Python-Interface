from __future__ import annotations

from .mydata_base import MyDataSection
from ..utils.data_conversion import convert_numeric_array_to_matlab
from ..utils.mydata_code_generation import generate_meta_data_code


class TypicalTemperatureSection(MyDataSection):
    key = "typical_temperature_block"

    def __init__(self, *, t_typical: int | float = 0, is_celsius: bool = False) -> None:
        self.t_typical = t_typical
        self.is_celsius = is_celsius
        converted_temperature = convert_numeric_array_to_matlab(self.t_typical)
        if self.is_celsius:
            converted_temperature = f"C2K({converted_temperature})"
        line = (
            f"{generate_meta_data_code('T_typical', converted_temperature).rstrip()} "
            "% K, body temperature"
        )
        super().__init__(matlab_code=line)


class SetTypicalTemperatureForAllDatasetsSection(MyDataSection):
    """
    This section provides code to set the temperature of all datasets to the typical temperature defined in
    `metadata.T_typical'.
    """
    key = "set_temperature_block"
    matlab_code = """%% Set temperature metadata
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};

    if ~isfield(temp, field)
        temp.(field) = metaData.T_typical;
        units.temp.(field) = 'K';
        label.temp.(field) = 'temperature';
    end
end"""
