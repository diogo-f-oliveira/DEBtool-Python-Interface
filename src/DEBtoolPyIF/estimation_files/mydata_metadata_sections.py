"""Metadata-oriented sections for mydata.m generation."""

from __future__ import annotations

from string import Template

from .mydata_base import BaseMyDataState, MyDataSection


class FunctionHeaderSection(MyDataSection):
    key = "function_header"

    def render(self, context, _state: BaseMyDataState) -> str:
        return Template(
            """function [data, auxData, metaData, txtData, weights] = mydata_${species_name}
% Baseline generic mydata template for DEBtoolPyIF.

data = struct();
auxData = struct();
metaData = struct();
txtData = struct();
weights = struct();
init = struct();
units = struct();
label = struct();
bibkey = struct();
comment = struct();
title = struct();
tiers = struct();
temp = struct();"""
        ).substitute(species_name=context.species_name)


class MetadataSection(MyDataSection):
    # TODO: Add arguments for metadata fields and use them in the render method.
    key = "metadata_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        return """%% set metaData
metaData.phylum     = '';
metaData.class      = '';
metaData.order      = '';
metaData.family     = '';
metaData.species    = '';
metaData.species_en = '';
metaData.T_typical  = 0; % K, body temperature
metaData.data_0     = {};
metaData.data_1     = {};

metaData.COMPLETE = 2.5; % using criteria of LikaKear2011

metaData.author   = {''};
% metaData.email    = {''};
% metaData.address  = {''};"""


class SaveFieldsSection(MyDataSection):
    key = "save_fields_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        return """%% Save dataset field names
metaData.data_fields = fieldnames(data);"""


class SaveDataFieldsByVariateTypeSection(MyDataSection):
    key = "data_partition_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        return """%% Save data fields into zero-variate and univariate
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};
    if length(data.(field)) > 1
        metaData.data_1{end+1} = field; %#ok<AGROW>
    else
        metaData.data_0{end+1} = field; %#ok<AGROW>
    end
end"""


class DiscussionSection(MyDataSection):
    # TODO: Add discussion points as arguments and build `metaData.discussion` with them.
    key = "discussion_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        return """
        %% Discussion points
D1 = '';
D2 = '';
metaData.discussion = struct('D1', D1, 'D2', D2);
"""


class BibkeysSection(MyDataSection):
    # TODO: Add arguments for bibliography keys and use them in the render method.
    # TODO: Take .bib file as input and copy bibliography info from file.
    key = "bibkeys_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        return "% Optional bibliography metadata can be inserted here."
