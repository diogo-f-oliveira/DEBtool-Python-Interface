"""Metadata-oriented sections for mydata.m generation."""

from __future__ import annotations

from .mydata_base import MyDataSection
from ..utils.data_conversion import (
    convert_numeric_array_to_matlab,
    convert_string_or_collection_to_matlab,
    convert_string_to_matlab,
)
from ..utils.mydata_code_generation import generate_meta_data_code


class MyDataFunctionHeaderSection(MyDataSection):
    key = "function_header"
    template_families = ("mydata",)
    matlab_code = """function [data, auxData, metaData, txtData, weights] = mydata_${species_name}
% Baseline generic mydata template for DEBtoolPyIF."""

    def __init__(self, *, species_name: str | None = None) -> None:
        self.species_name = species_name
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        if self.species_name is None:
            return {}
        return {"species_name": self.species_name}

    def get_render_substitutions(self, context, state=None) -> dict[str, str]:
        if self.species_name is not None:
            return {}
        return {"species_name": context.species_name}


class SpeciesInfoMetadataSection(MyDataSection):
    key = "metadata_block"
    template_families = ("mydata",)
    section_tags = ("metadata",)

    def __init__(
        self,
        *,
        phylum: str = "",
        class_name: str = "",
        order_name: str = "",
        family: str = "",
        species: str = "",
        species_en: str = "",
        t_typical: int | float = 0,
        complete: int | float = 2.5,
    ) -> None:
        self.phylum = phylum
        self.class_name = class_name
        self.order_name = order_name
        self.family = family
        self.species = species
        self.species_en = species_en
        self.t_typical = t_typical
        self.complete = complete
        lines = [
            "%% set metaData",
            generate_meta_data_code("phylum", convert_string_to_matlab(self.phylum)).rstrip(),
            generate_meta_data_code("class", convert_string_to_matlab(self.class_name)).rstrip(),
            generate_meta_data_code("order", convert_string_to_matlab(self.order_name)).rstrip(),
            generate_meta_data_code("family", convert_string_to_matlab(self.family)).rstrip(),
            generate_meta_data_code("species", convert_string_to_matlab(self.species)).rstrip(),
            generate_meta_data_code("species_en", convert_string_to_matlab(self.species_en)).rstrip(),
        ]
        super().__init__(matlab_code="\n".join(lines))


class CompletenessLevelSection(MyDataSection):
    key = "completeness_level_block"
    template_families = ("mydata",)
    section_tags = ("metadata",)

    def __init__(self, *, complete: int | float = 2.5) -> None:
        self.complete = complete
        line = (
            f"{generate_meta_data_code('COMPLETE', convert_numeric_array_to_matlab(self.complete)).rstrip()} "
            "% using criteria of LikaKear2011"
        )
        super().__init__(matlab_code=line)

class AuthorInfoMetadataSection(MyDataSection):
    key = "author_info_block"
    template_families = ("mydata",)
    section_tags = ("metadata",)

    def __init__(
        self,
        *,
        author: str | list[str] | tuple[str, ...] = "",
        email: str | list[str] | tuple[str, ...] = "",
        address: str | list[str] | tuple[str, ...] = "",
    ) -> None:
        self.author = author
        self.email = email
        self.address = address
        lines = [
            "%% Author information",
            generate_meta_data_code("author", convert_string_or_collection_to_matlab(self.author)).rstrip(),
            generate_meta_data_code('email', convert_string_or_collection_to_matlab(self.email)).rstrip(),
            generate_meta_data_code('address', convert_string_or_collection_to_matlab(self.address)).rstrip(),
        ]
        super().__init__(matlab_code="\n".join(lines))

class SaveFieldsSection(MyDataSection):
    key = "save_fields_block"
    template_families = ("mydata",)
    section_tags = ("metadata",)
    matlab_code = """%% Save dataset field names
metaData.data_fields = fieldnames(data);"""


class SaveDataFieldsByVariateTypeSection(MyDataSection):
    key = "save_fields_by_variate_type_block"
    template_families = ("mydata",)
    section_tags = ("metadata",)
    matlab_code = """%% Save data fields into zero-variate and univariate
metaData.data_0     = {};
metaData.data_1     = {};
for i = 1:length(metaData.data_fields)
    field = metaData.data_fields{i};
    if length(data.(field)) > 1
        metaData.data_1{end+1} = field; %#ok<AGROW>
    else
        metaData.data_0{end+1} = field; %#ok<AGROW>
    end
end"""


class DiscussionSection(MyDataSection):
    key = "discussion_block"
    template_families = ("mydata",)
    section_tags = ("metadata",)
    matlab_code = """%% Discussion points
${discussion_assignments}
metaData.discussion = struct(${discussion_struct});
"""

    def __init__(self, *, discussion_points: dict[str, str] | None = None) -> None:
        self.discussion_points = {"D1": "", "D2": ""} if discussion_points is None else discussion_points
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        assignments = "\n".join(
            f"{key} = {convert_string_to_matlab(value)};"
            for key, value in self.discussion_points.items()
        )
        struct_entries = ", ".join(f"'{key}', {key}" for key in self.discussion_points)
        return {
            "discussion_assignments": assignments,
            "discussion_struct": struct_entries,
        }


class BibkeysSection(MyDataSection):
    key = "bibkeys_block"
    template_families = ("mydata",)
    section_tags = ("metadata",)
    matlab_code = "${bibkeys_content}"

    def __init__(self, *, bibkeys_content: str = "% Optional bibliography metadata can be inserted here.") -> None:
        self.bibkeys_content = bibkeys_content
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        return {"bibkeys_content": self.bibkeys_content}
