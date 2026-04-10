"""Packing and output sections for mydata.m generation."""

from __future__ import annotations

from .mydata_base import MyDataSection


class PackingSection(MyDataSection):
    key = "packing_block"
    matlab_code = """%% pack auxData and txtData for output
auxData.temp = temp;
auxData.init = init;
txtData.units = units;
txtData.label = label;
txtData.bibkey = bibkey;
txtData.comment = comment;
txtData.title = title;

end"""
