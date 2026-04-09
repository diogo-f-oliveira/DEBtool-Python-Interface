"""Packing and output sections for mydata.m generation."""

from __future__ import annotations

from .mydata_base import BaseMyDataState, MyDataSection


class PackingSection(MyDataSection):
    # TODO: Take as input structs and target structs for packing and generate code accordingly.
    key = "packing_block"

    def render(self, _context, _state: BaseMyDataState) -> str:
        lines = [
            "%% pack auxData and txtData for output",
            "auxData.temp = temp;",
            "auxData.init = init;",
            "txtData.units = units;",
            "txtData.label = label;",
            "txtData.bibkey = bibkey;",
            "txtData.comment = comment;",
            "txtData.title = title;",
            "",
            "end",
        ]
        return "\n".join(lines)
