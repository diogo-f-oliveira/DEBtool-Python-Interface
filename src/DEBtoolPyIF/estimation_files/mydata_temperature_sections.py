from __future__ import annotations

from DEBtoolPyIF import MyDataSection


class SetTypicalTemperatureForAllDatasetsSection(MyDataSection):
    """
    This section provides code to set the temperature of all datasets to the typical temperature defined in
    `metadata.T_typical'.
    """
    key = "set_temperature_block"
    matlab_code = """%% Set temperature metadata
temp = struct();
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};

    if ~isfield(temp, field)
        temp.(field) = metaData.T_typical;
        units.temp.(field) = 'K';
        label.temp.(field) = 'temperature';
    end
end"""
