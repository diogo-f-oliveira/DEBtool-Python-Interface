"""Multitier-specific mydata template families."""

from __future__ import annotations

from pathlib import Path

from ..estimation_files.mydata import (
    MyDataProgrammaticTemplate,
    MyDataSubstitutionTemplate,
    MyDataTemplate,
)
from ..estimation_files.mydata_base import BaseMyDataState, MyDataSection
from ..estimation_files.mydata_data_sections import (
    EntityDataSection,
    ExtraInfoSection,
    GroupDataSection,
)
from ..estimation_files.mydata_metadata_sections import (
    BibkeysSection,
    CompletenessLevelSection,
    DiscussionSection,
    MyDataFunctionHeader,
    SaveDataFieldsByVariateTypeSection,
    SaveFieldsSection,
    SpeciesInfoMetadataSection,
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
from .mydata_sections import (
    EntityDescendantsSection,
    EntityPathSection,
    MultitierEntityListSection,
    MultitierGroupsOfEntitySection,
    MultitierPackingSection,
    MultitierPseudoDataSection,
    TierEntitiesSection,
    TierGroupsSection,
    TierParInitValuesSection,
    TierParsSection,
    build_multitier_mydata_state,
)

class MultitierMyDataTemplate(MyDataTemplate):
    """Shared file-family behavior for multitier mydata templates."""

    template_families = ("mydata", "multitier_mydata")

    @classmethod
    def tier_variable_sections(cls) -> tuple[MyDataSection, ...]:
        return (
            MultitierEntityListSection(),
            TierEntitiesSection(),
            TierGroupsSection(),
            MultitierGroupsOfEntitySection(),
            EntityDescendantsSection(),
            EntityPathSection(),
            TierParsSection(),
            TierParInitValuesSection(),
        )

    @classmethod
    def default_sections(cls) -> tuple[MyDataSection, ...]:
        return (
            MyDataFunctionHeader(),
            SpeciesInfoMetadataSection(),
            TypicalTemperatureSection(),
            CompletenessLevelSection(),
            *cls.data_sections(),
            *cls.tier_variable_sections(),
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
            MyDataFunctionHeader(),
            SpeciesInfoMetadataSection(),
            TypicalTemperatureSection(),
            CompletenessLevelSection(),
            GroupDataSection(),
            EntityDataSection(),
            *cls.tier_variable_sections(),
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
            allowed_section_keys=self.allowed_section_keys(),
            required_section_keys=self.required_section_keys(),
            template_label=self.template_label,
        )


class MultitierMyDataSubstitutionTemplate(MultitierMyDataTemplate, MyDataSubstitutionTemplate):
    """Source-backed multitier mydata template with construction-time section matching."""

    def __init__(self, *, source: str | Path, sections: tuple[MyDataSection, ...] | None = None) -> None:
        MyDataSubstitutionTemplate.__init__(self, source=source, sections=sections)
