"""Multitier-specific mydata template families."""

from __future__ import annotations

from pathlib import Path

from ..estimation_files.mydata import (
    MYDATA_BASE_REQUIRED_TEMPLATE_KEYS,
    MYDATA_TEMPLATE_KEYS,
    MyDataProgrammaticTemplate,
    MyDataSubstitutionTemplate,
    MyDataTemplate,
)
from ..estimation_files.mydata_base import BaseMyDataState, MyDataSection
from ..estimation_files.mydata_data_sections import (
    EntityDataSection,
    EntityDataTypesSection,
    ExtraInfoSection,
    GroupDataSection,
    GroupDataTypesSection,
)
from ..estimation_files.mydata_metadata_sections import (
    CompletenessLevelSection,
    DiscussionSection,
    MyDataFunctionHeaderSection,
    SpeciesInfoMetadataSection,
    SaveDataFieldsByVariateTypeSection,
    SaveFieldsSection, BibkeysSection,
)
from ..estimation_files.mydata_pseudodata_sections import AddPseudoDataSection
from ..estimation_files.mydata_weight_sections import (
    RemoveDummyWeightsSection,
    InitializeWeightsSection,
)
from ..estimation_files.mydata_temperature_sections import (
    SetTypicalTemperatureForAllDatasetsSection,
    TypicalTemperatureSection,
)
from ..estimation_files.templates import ProgrammaticTemplate
from ..utils.data_conversion import convert_dict_to_matlab, convert_list_of_strings_to_matlab
from ..utils.mydata_code_generation import generate_tier_variable_code
from .mydata_sections import (
    MultitierPackingSection,
    MultitierPseudoDataSection,
    TierEntitiesSection,
    TierGroupsSection,
    TierParInitValuesSection,
    TierParsSection,
    TierSubtreeSection,
    build_multitier_mydata_state,
)


MULTITIER_MYDATA_TEMPLATE_KEYS = MYDATA_TEMPLATE_KEYS + (
    "entity_list",
    "tier_entities",
    "tier_groups",
    "groups_of_entity",
    "tier_subtree",
    "tier_pars",
    "tier_par_init_values",
    "multitier_pseudodata_block",
)

MULTITIER_MYDATA_REQUIRED_TEMPLATE_KEYS = MYDATA_BASE_REQUIRED_TEMPLATE_KEYS + (
    "multitier_pseudodata_block",
    "entity_list",
    "tier_entities",
    "tier_groups",
    "groups_of_entity",
    "tier_subtree",
    "tier_pars",
    "tier_par_init_values",
)


class EntityListSection(MyDataSection):
    key = "entity_list"

    def render(self, _context, state: BaseMyDataState) -> str:
        if not state.entity_list:
            return ""
        return generate_tier_variable_code(
            var_name="entity_list",
            converted_data=convert_list_of_strings_to_matlab(list(state.entity_list)),
            label="List of entities",
            pars_init_access=True,
        )


class GroupsOfEntitySection(MyDataSection):
    key = "groups_of_entity"

    def render(self, _context, state: BaseMyDataState) -> str:
        if not state.groups_of_entity:
            return ""
        return generate_tier_variable_code(
            var_name="groups_of_entity",
            converted_data=convert_dict_to_matlab(
                {
                    entity_id: convert_list_of_strings_to_matlab(group_ids, double_brackets=True)
                    for entity_id, group_ids in state.groups_of_entity.items()
                }
            ),
            label="Groups each entity belongs to",
        )


class MultitierMyDataTemplate(MyDataTemplate):
    """Shared file-family behavior for multitier mydata templates."""

    allowed_section_keys = MULTITIER_MYDATA_TEMPLATE_KEYS
    required_section_keys = MULTITIER_MYDATA_REQUIRED_TEMPLATE_KEYS

    @classmethod
    def default_sections(cls) -> tuple[MyDataSection, ...]:
        return (
            MyDataFunctionHeaderSection(),
            SpeciesInfoMetadataSection(),
            TypicalTemperatureSection(),
            CompletenessLevelSection(),
            GroupDataSection(),
            GroupDataTypesSection(),
            EntityDataSection(),
            EntityDataTypesSection(),
            EntityListSection(),
            TierEntitiesSection(),
            TierGroupsSection(),
            GroupsOfEntitySection(),
            TierSubtreeSection(),
            TierParsSection(),
            TierParInitValuesSection(),
            ExtraInfoSection(),
            InitializeWeightsSection(),
            SaveFieldsSection(),
            SetTypicalTemperatureForAllDatasetsSection(),
            RemoveDummyWeightsSection(),
            SaveDataFieldsByVariateTypeSection(),
            AddPseudoDataSection(),
            MultitierPseudoDataSection(),
            BibkeysSection(),
            DiscussionSection(),
            MultitierPackingSection(),
        )

    @classmethod
    def required_sections(cls) -> tuple[MyDataSection, ...]:
        return (
            MyDataFunctionHeaderSection(),
            SpeciesInfoMetadataSection(),
            TypicalTemperatureSection(),
            CompletenessLevelSection(),
            GroupDataSection(),
            EntityDataSection(),
            EntityListSection(),
            TierEntitiesSection(),
            TierGroupsSection(),
            GroupsOfEntitySection(),
            TierSubtreeSection(),
            TierParsSection(),
            TierParInitValuesSection(),
            InitializeWeightsSection(),
            SaveFieldsSection(),
            RemoveDummyWeightsSection(),
            AddPseudoDataSection(),
            MultitierPseudoDataSection(),
            MultitierPackingSection(),
        )

    def build_state(self, context) -> BaseMyDataState:
        return build_multitier_mydata_state(context)


class MultitierMyDataProgrammaticTemplate(MultitierMyDataTemplate, MyDataProgrammaticTemplate):
    """Validated direct-assembly programmatic multitier mydata template."""

    def __init__(self, *, sections: tuple[MyDataSection, ...] | None = None) -> None:
        final_sections = self.required_sections() if sections is None else tuple(sections)
        ProgrammaticTemplate.__init__(
            self,
            sections=final_sections,
            allowed_section_keys=self.allowed_section_keys,
            required_section_keys=self.required_section_keys,
            template_label=self.template_label,
        )


class MultitierMyDataSubstitutionTemplate(MultitierMyDataTemplate, MyDataSubstitutionTemplate):
    """Source-backed multitier mydata template with construction-time section matching."""

    def __init__(self, *, source: str | Path, sections: tuple[MyDataSection, ...] | None = None) -> None:
        MyDataSubstitutionTemplate.__init__(self, source=source, sections=sections)
