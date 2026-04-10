"""mydata.m template families and shared section helpers."""

from __future__ import annotations

from pathlib import Path

from .mydata_base import BaseMyDataState, MyDataSection
from .mydata_data_sections import (
    EntityDataSection,
    EntityDataTypesSection,
    ExtraInfoSection,
    GroupDataSection,
    GroupDataTypesSection,
)
from .mydata_metadata_sections import (
    BibkeysSection,
    CompletenessLevelSection,
    DiscussionSection,
    MyDataFunctionHeaderSection,
    SpeciesInfoMetadataSection,
    SaveFieldsSection,
)
from .mydata_packing_sections import PackingSection
from .mydata_pseudodata_sections import AddPseudoDataSection
from .mydata_temperature_sections import TypicalTemperatureSection
from .mydata_weight_sections import RemoveDummyWeightsSection, InitializeWeightsSection
from .templates import ProgrammaticTemplate, SubstitutionTemplate


MYDATA_TEMPLATE_KEYS = (
    "function_header",
    "metadata_block",
    "typical_temperature_block",
    "completeness_level_block",
    "group_data_block",
    "group_data_types",
    "entity_data_block",
    "entity_data_types",
    "extra_info",
    "weights_block",
    "save_fields_block",
    "set_temperature_block",
    "remove_dummy_weights_block",
    "data_partition_block",
    "add_pseudodata_block",
    "bibkeys_block",
    "discussion_block",
    "packing_block",
)

MYDATA_BASE_REQUIRED_TEMPLATE_KEYS = (
    "function_header",
    "metadata_block",
    "typical_temperature_block",
    "completeness_level_block",
    "entity_data_block",
    "group_data_block",
    "weights_block",
    "save_fields_block",
    "remove_dummy_weights_block",
    "add_pseudodata_block",
    "packing_block",
)


def build_mydata_state(context) -> BaseMyDataState:
    """Build the base mydata state from context data only."""

    return BaseMyDataState(
        entity_data_blocks=tuple(getattr(context, "entity_data_blocks", ())),
        group_data_blocks=tuple(getattr(context, "group_data_blocks", ())),
        entity_data_types=tuple(getattr(context, "entity_data_types", ())),
        group_data_types=tuple(getattr(context, "group_data_types", ())),
        entity_list=tuple(getattr(context, "entity_list", ())),
        groups_of_entity=dict(getattr(context, "groups_of_entity", {})),
        extra_info=getattr(context, "extra_info", ""),
    )


def build_mydata_substitutions(
    context,
    sections: tuple[MyDataSection, ...],
    *,
    state: BaseMyDataState | None = None,
) -> dict[str, str]:
    """Build a substitution map from mydata sections."""

    if state is None:
        state = build_mydata_state(context)
    substitutions = {}
    for section in sections:
        substitutions[section.key] = section.render(context, state)
    return substitutions


class MyDataTemplate:
    """Shared file-family behavior for mydata template classes."""

    template_label = "mydata"
    allowed_section_keys = MYDATA_TEMPLATE_KEYS
    required_section_keys = MYDATA_BASE_REQUIRED_TEMPLATE_KEYS

    @classmethod
    def data_sections(cls) -> tuple[MyDataSection, ...]:
        return (
            GroupDataSection(),
            GroupDataTypesSection(),
            EntityDataSection(),
            EntityDataTypesSection(),
        )

    @classmethod
    def default_sections(cls) -> tuple[MyDataSection, ...]:
        return (
            MyDataFunctionHeaderSection(),
            SpeciesInfoMetadataSection(),
            TypicalTemperatureSection(),
            CompletenessLevelSection(),
            *cls.data_sections(),
            ExtraInfoSection(),
            InitializeWeightsSection(),
            SaveFieldsSection(),
            # SetTemperatureSection(),
            RemoveDummyWeightsSection(),
            # SaveDataFieldsByVariateTypeSection(),
            AddPseudoDataSection(),
            BibkeysSection(),
            DiscussionSection(),
            PackingSection(),
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
            InitializeWeightsSection(),
            SaveFieldsSection(),
            RemoveDummyWeightsSection(),
            AddPseudoDataSection(),
            PackingSection(),
        )

    def get_section_key(self, section) -> str:
        return section.key

    def build_state(self, context) -> BaseMyDataState:
        return build_mydata_state(context)

    def render_section_with_state(self, section, context, state: BaseMyDataState) -> str:
        return section.render(context, state)

    def render_section(self, section, context) -> str:
        return self.render_section_with_state(section, context, self.build_state(context))


class MyDataProgrammaticTemplate(MyDataTemplate, ProgrammaticTemplate):
    """Validated direct-assembly programmatic mydata template."""

    def __init__(self, *, sections: tuple[MyDataSection, ...] | None = None) -> None:
        final_sections = self.required_sections() if sections is None else tuple(sections)
        super().__init__(
            sections=final_sections,
            allowed_section_keys=self.allowed_section_keys,
            required_section_keys=self.required_section_keys,
            template_label=self.template_label,
        )

    def render(self, context) -> str:
        self.validate(context)
        state = self.build_state(context)
        rendered_sections: list[str] = []
        for section in self.get_sections():
            output = self.render_section_with_state(section, context, state).rstrip()
            if output:
                rendered_sections.append(output)
        return "\n\n".join(rendered_sections)


class MyDataSubstitutionTemplate(MyDataTemplate, SubstitutionTemplate):
    """Source-backed mydata template with construction-time section matching."""

    def __init__(self, *, source: str | Path, sections: tuple[MyDataSection, ...] | None = None) -> None:
        super().__init__(
            source=source,
            sections=sections,
            template_label=self.template_label,
        )

    def get_default_sections(self) -> tuple:
        return self.default_sections()

    def build_substitutions(self, context) -> dict[str, str]:
        state = self.build_state(context)
        return {
            self.get_section_key(section): self.render_section_with_state(section, context, state)
            for section in self.get_sections()
        }
