"""Packing and output sections for mydata.m generation."""

from __future__ import annotations

from .mydata_base import MyDataSection

# TODO: Transform into a general "packing" section that can be used in multiple template families, and convert this module to a generic packing_sections module.
# TODO: Add subclasses for each template family

class PackingSection(MyDataSection):
    key = "packing_block"
    template_families = ("mydata",)
    section_tags = ("packing",)

    def __init__(
        self,
        *,
        aux_data_fields: list[str] | tuple[str, ...] = ("temp",),
        txt_data_fields: list[str] | tuple[str, ...] = ("units", "label", "bibkey", "comment", "title"),
    ) -> None:
        self.aux_data_fields = tuple(aux_data_fields)
        self.txt_data_fields = tuple(txt_data_fields)

        aux_lines = [f"auxData.{field_name} = {field_name};" for field_name in self.aux_data_fields]
        txt_lines = [f"txtData.{field_name} = {field_name};" for field_name in self.txt_data_fields]

        lines = ["%% pack auxData and txtData for output", *aux_lines, *txt_lines, "", "end"]
        super().__init__(matlab_code="\n".join(lines))
