"""Pseudo-data sections for mydata.m generation."""

from __future__ import annotations

from .mydata_base import MyDataSection


class AddPseudoDataSection(MyDataSection):
    key = "add_pseudodata_block"
    matlab_code = """%% Add generic pseudo-data
[data, units, label, weights] = addpseudodata(data, units, label, weights);"""
