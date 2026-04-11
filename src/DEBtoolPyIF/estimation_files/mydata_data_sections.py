"""Data-oriented sections for mydata.m generation."""

from __future__ import annotations

from ..utils.data_conversion import convert_list_of_strings_to_matlab
from ..utils.mydata_code_generation import generate_meta_data_code
from .mydata_base import BaseMyDataState, MyDataSection


class GroupDataSection(MyDataSection):
    key = "group_data_block"
    template_families = ("mydata",)
    section_tags = ("data",)

    def render(self, _context, state: BaseMyDataState) -> str:
        return "\n".join(state.group_data_blocks)


class GroupDataTypesSection(MyDataSection):
    key = "group_data_types"
    template_families = ("mydata",)
    section_tags = ("data",)

    def render(self, _context, state: BaseMyDataState) -> str:
        if not state.group_data_types:
            return ""
        return generate_meta_data_code(
            var_name="group_data_types",
            converted_data=convert_list_of_strings_to_matlab(list(state.group_data_types)),
        )


class EntityDataSection(MyDataSection):
    key = "entity_data_block"
    template_families = ("mydata",)
    section_tags = ("data",)

    def render(self, _context, state: BaseMyDataState) -> str:
        return "\n".join(state.entity_data_blocks)


class EntityDataTypesSection(MyDataSection):
    key = "entity_data_types"
    template_families = ("mydata",)
    section_tags = ("data",)

    def render(self, _context, state: BaseMyDataState) -> str:
        if not state.entity_data_types:
            return ""
        return generate_meta_data_code(
            var_name="entity_data_types",
            converted_data=convert_list_of_strings_to_matlab(list(state.entity_data_types)),
        )


class ExtraInfoSection(MyDataSection):
    key = "extra_info"
    template_families = ("mydata",)
    section_tags = ("extra_info",)

    def render(self, _context, state: BaseMyDataState) -> str:
        return state.extra_info
