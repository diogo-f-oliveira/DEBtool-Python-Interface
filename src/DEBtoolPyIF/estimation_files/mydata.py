"""mydata.m template families and shared section helpers."""

from __future__ import annotations

from pathlib import Path

from .mydata_base import BaseMyDataState, MyDataSection
from .mydata_data_sections import (
    EntityDataSection,
    ExtraInfoSection,
    GroupDataSection,
)
from .mydata_metadata_sections import (
    BibkeysSection,
    CompletenessLevelSection,
    DiscussionSection,
    MyDataFunctionHeader,
    SpeciesInfoMetadataSection,
    SaveFieldsSection,
)
from .mydata_packing_sections import PackingSection
from .mydata_pseudodata_sections import AddPseudoDataSection
from .mydata_temperature_sections import TypicalTemperatureSection
from .mydata_weight_sections import RemoveDummyWeightsSection, InitializeWeightsSection
from .templates import ProgrammaticTemplate, SubstitutionTemplate


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
    template_families = ("mydata",)

    @classmethod
    def available_section_classes(cls) -> tuple[type[MyDataSection], ...]:
        return MyDataSection.registered_section_classes(
            template_families=cls.template_families,
        )

    @classmethod
    def allowed_section_keys(cls) -> tuple[str, ...]:
        return tuple(dict.fromkeys(section_class.key for section_class in cls.available_section_classes()))

    @classmethod
    def required_section_keys(cls) -> tuple[str, ...]:
        return tuple(section.key for section in cls.required_sections())

    @classmethod
    def section_classes_for_tag(cls, tag: str) -> tuple[type[MyDataSection], ...]:
        return MyDataSection.registered_section_classes(
            template_families=cls.template_families,
            tag=tag,
        )

    @classmethod
    def sections_for_tag(cls, tag: str) -> tuple[MyDataSection, ...]:
        return tuple(section_class() for section_class in cls.section_classes_for_tag(tag))

    @classmethod
    def data_sections(cls) -> tuple[MyDataSection, ...]:
        return cls.sections_for_tag("data")

    @classmethod
    def default_sections(cls) -> tuple[MyDataSection, ...]:
        return (
            MyDataFunctionHeader(),
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
            MyDataFunctionHeader(),
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
            allowed_section_keys=self.allowed_section_keys(),
            required_section_keys=self.required_section_keys(),
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
