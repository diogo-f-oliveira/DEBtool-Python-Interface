"""Pseudo-data sections for mydata.m generation."""

from __future__ import annotations

from .mydata_base import BaseMyDataState, MyDataSection


class AddPseudoDataSection(MyDataSection):
    key = "add_pseudodata_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        return """%% Add generic pseudo-data
[data, units, label, weights] = addpseudodata(data, units, label, weights);"""
