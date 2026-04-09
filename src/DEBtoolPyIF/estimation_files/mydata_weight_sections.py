"""Weight and temperature sections for mydata.m generation."""

from __future__ import annotations

from .mydata_base import BaseMyDataState, MyDataSection


class InitializeWeightsSection(MyDataSection):
    key = "weights_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        return """%% Set default weights
weights = setweights(data, []);"""


class RemoveDummyWeightsSection(MyDataSection):
    key = "remove_dummy_weights_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        return """%% Remove weights from dummy variables
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};
    if strcmp(label.(field), 'Dummy variable')
        weights.(field) = 0;
    end
end"""
