"""Weight and temperature sections for mydata.m generation."""

from __future__ import annotations

from .mydata_base import MyDataSection


class InitializeWeightsSection(MyDataSection):
    key = "weights_block"
    template_families = ("mydata",)
    section_tags = ("weights",)
    matlab_code = """%% Set default weights
weights = setweights(data, []);"""


class RemoveDummyWeightsSection(MyDataSection):
    key = "remove_dummy_weights_block"
    template_families = ("mydata",)
    section_tags = ("weights",)
    matlab_code = """%% Remove weights from dummy variables
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};
    if strcmp(label.(field), 'Dummy variable')
        weights.(field) = 0;
    end
end"""
