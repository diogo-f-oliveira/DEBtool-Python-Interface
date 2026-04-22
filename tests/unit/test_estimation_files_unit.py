from importlib import resources
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from DEBtoolPyIF.estimation_files import (
    AddPathSection,
    AlgorithmRunTemplate,
    BaseMyDataState,
    CopyFileTemplate,
    EstimationFileSection,
    EstimationTemplates,
    EstimOption,
    IntegerEstimOption,
    MyDataSection,
    MyDataProgrammaticTemplate,
    MyDataSubstitutionTemplate,
    NumericEstimOption,
    ParsInitProgrammaticTemplate,
    ParsInitChemicalParametersSection,
    ParsInitReferenceTemperatureSection,
    ParsInitSection,
    ParsInitSubstitutionTemplate,
    ProgrammaticTemplate,
    RegistryParsInitProgrammaticTemplate,
    RegistryParsInitSubstitutionTemplate,
    SetEstimOptionsSection,
    RunProgrammaticTemplate,
    RunSection,
    RunSetting,
    RunSubstitutionTemplate,
    SetDefaultEstimOptions,
    SetFilterOption,
    SetMaxFunEvalsOption,
    SetMaxStepNumberOption,
    SetMethodOption,
    SetParsInitMethodOption,
    SetResultsOutputOption,
    SetSimplexSizeOption,
    SetTolSimplexOption,
    StringEstimOption,
    build_mydata_substitutions,
    normalize_estimation_templates,
)
from DEBtoolPyIF.estimation_files.algorithms import AlternatingRestartNelderMead, NelderMead, RestartingNelderMead
from DEBtoolPyIF.estimation_files.mydata import MyDataTemplate
from DEBtoolPyIF.estimation_files.mydata_data_sections import (
    EntityDataSection,
    EntityDataTypesSection,
    EntityListSection,
    ExtraInfoSection,
    GroupsOfEntitySection,
    GroupDataSection,
    GroupDataTypesSection,
)
from DEBtoolPyIF.estimation_files.mydata_metadata_sections import (
    AuthorInfoMetadataSection,
    CompletenessLevelSection,
    MyDataFunctionHeader,
    SpeciesInfoMetadataSection,
)
from DEBtoolPyIF.estimation_files.mydata_packing_sections import PackingSection
from DEBtoolPyIF.estimation_files.mydata_temperature_sections import TypicalTemperatureSection
from DEBtoolPyIF.estimation_files.pars_init import ParsInitFunctionHeader, ParsInitTemplate
from DEBtoolPyIF.estimation_files.pars_init_sections import ParsInitAddChemSection
from DEBtoolPyIF.estimation_files.run_sections import RestartLoopSection
from DEBtoolPyIF.multitier.pars_init import build_registry_multitier_pars_init_sections
from DEBtoolPyIF.multitier import (
    MultiTierStructure,
    MultitierMyDataProgrammaticTemplate,
    MultitierMyDataSubstitutionTemplate,
    MultitierParsInitProgrammaticTemplate,
    MultitierParsInitSubstitutionTemplate,
    RegistryMultitierParsInitProgrammaticTemplate,
    RegistryMultitierParsInitSubstitutionTemplate,
    TierHierarchy,
    build_estimation_templates_from_folder,
)
from DEBtoolPyIF.multitier.estimation_files import MultitierGenerationContext
from DEBtoolPyIF.multitier.mydata import MultitierMyDataTemplate
from DEBtoolPyIF.multitier.mydata_sections import (
    MultitierEntityListSection,
    MultitierGroupsOfEntitySection,
    TierEntitiesSection,
    TierGroupsSection,
    TierParInitValuesSection,
    TierParsSection,
    TierSubtreeSection,
)
from DEBtoolPyIF.parameters import (
    ALL_PARAMETER_DEFINITIONS,
    ChemicalParameters,
    DEFAULT_PARAMETER_DEFINITIONS,
    PARAMETER_DEFINITIONS_BY_NAME,
    E_Hx,
    ParameterDefinition,
    ParameterRegistry,
    StdParameterRegistry,
    StxParameterRegistry,
    del_M,
    get_chemical_parameter_values_of,
    get_chemical_parameters_of,
    get_parameter_definition,
    p_Am,
    require_parameter_definition,
    t_0,
)
from DEBtoolPyIF.parameters.chemical import (
    CarbonChemicalIndexDefinition,
    ChemicalParameterValues,
    ChemicalPotentialDefinition,
    HydrogenChemicalIndexDefinition,
    NitrogenChemicalIndexDefinition,
    OxygenChemicalIndexDefinition,
)
import DEBtoolPyIF.parameters.registry as parameter_registry_module
import DEBtoolPyIF.parameters.definitions as parameter_definitions_module
import DEBtoolPyIF.parameters as parameters_package


class FakeTierData:
    def __init__(self, entity_data_types=None, group_data_types=None):
        self.groups = []
        self.entities = ["entity_1"]
        self.entity_data_types = entity_data_types or ["obs"]
        self.group_data_types = group_data_types or []


class FakeCodegenTierData:
    def __init__(self, entity_data_types, group_data_types):
        self._entity_data_types = entity_data_types
        self._group_data_types = group_data_types

    def get_group_list_from_entity_list(self, entity_list):
        del entity_list
        return []

    def get_entity_mydata_code(self, entity_list):
        del entity_list
        return list(self._entity_data_types), ["% entity data"]

    def get_group_mydata_code(self, entity_list):
        del entity_list
        return list(self._group_data_types), ["% group data"]

    def get_groups_of_entities(self, entity_list):
        return {entity_id: [] for entity_id in entity_list}


class FakeCodegenTierStructure:
    def __init__(self):
        self.species_name = "Test_species"
        self.entity_hierarchy = TierHierarchy(
            tier_names=["top", "bottom"],
            entities={
                "top": ["root_entity"],
                "bottom": ["child_b", "child_a"],
            },
            parents={
                "bottom": {
                    "child_b": "root_entity",
                    "child_a": "root_entity",
                },
            },
        )
        self.tiers = {
            "top": SimpleNamespace(
                data=FakeCodegenTierData(
                    entity_data_types=["zeta", "alpha", "zeta"],
                    group_data_types=["group_z", "group_a", "group_z"],
                )
            ),
            "bottom": SimpleNamespace(
                data=FakeCodegenTierData(
                    entity_data_types=["beta", "alpha"],
                    group_data_types=["group_m", "group_a"],
                )
            ),
        }

    def get_init_par_values(self, tier_name, entity_list):
        del tier_name
        return pd.DataFrame({"par_a": [1.0]}, index=list(entity_list))

    def get_full_pars_dict(self, tier_name, entity_id):
        del tier_name, entity_id
        return {"p_Am": 12.5, "kap_X": 0.25, "del_M": 0.15}


def _write_tier_template_folder(base_folder: Path, tier_name: str, species_name: str):
    tier_folder = base_folder / tier_name
    tier_folder.mkdir(parents=True)
    for prefix in ("mydata", "pars_init", "predict", "run"):
        (tier_folder / f"{prefix}_{species_name}.m").write_text("% template\n", encoding="utf-8")
    return tier_folder


class InlineMyDataSection(MyDataSection):
    def __init__(self, *, key: str, content: str):
        self.key = key
        super().__init__(matlab_code=content)


class InlineEstimationSection(EstimationFileSection):
    def __init__(self, *, slot_name: str, content: str):
        self.slot_name = slot_name
        super().__init__(matlab_code=content)


class InlineParsInitSection(ParsInitSection):
    def __init__(self, *, key: str, content: str):
        self.key = key
        super().__init__(matlab_code=content)


class InlineRunSection(RunSection):
    def __init__(self, *, key: str, content: str):
        self.key = key
        super().__init__(matlab_code=content)


def test_estimation_templates_from_mapping_accept_template_instances(tmp_path):
    predict_path = tmp_path / "predict_Test_species.m"
    predict_path.write_text("% predict template\n", encoding="utf-8")

    estimation_templates = EstimationTemplates.from_mapping(
        {
            "mydata": MyDataSubstitutionTemplate(source="mydata template"),
            "pars_init": ParsInitSubstitutionTemplate(source="pars_init template"),
            "predict": CopyFileTemplate(predict_path),
            "run": RunSubstitutionTemplate(source="run template"),
        }
    )

    assert isinstance(estimation_templates.mydata, MyDataSubstitutionTemplate)
    assert isinstance(estimation_templates.pars_init, ParsInitSubstitutionTemplate)
    assert isinstance(estimation_templates.predict, CopyFileTemplate)
    assert isinstance(estimation_templates.run, RunSubstitutionTemplate)


def test_estimation_templates_from_mapping_coerces_matlab_path_strings_to_copy_templates(tmp_path):
    mydata_path = str(tmp_path / "mydata_Test_species.m")
    pars_init_path = str(tmp_path / "pars_init_Test_species.m")
    predict_path = str(tmp_path / "predict_Test_species.m")
    run_path = str(tmp_path / "run_Test_species.m")

    estimation_templates = EstimationTemplates.from_mapping(
        {
            "mydata": mydata_path,
            "pars_init": pars_init_path,
            "predict": predict_path,
            "run": run_path,
        }
    )

    assert isinstance(estimation_templates.mydata, CopyFileTemplate)
    assert estimation_templates.mydata.path == mydata_path
    assert isinstance(estimation_templates.pars_init, CopyFileTemplate)
    assert isinstance(estimation_templates.predict, CopyFileTemplate)
    assert isinstance(estimation_templates.run, CopyFileTemplate)


def test_estimation_templates_from_mapping_rejects_non_matlab_path_strings():
    with pytest.raises(TypeError, match="MATLAB '.m' file paths"):
        EstimationTemplates.from_mapping(
            {
                "mydata": "mydata template",
                "pars_init": "pars_init_Test_species.m",
                "predict": "predict_Test_species.m",
                "run": "run_Test_species.m",
            }
        )


def test_normalize_estimation_templates_reject_invalid_template_keys():
    with pytest.raises(ValueError, match="Unknown estimation template keys"):
        normalize_estimation_templates(
            estimation_templates={
                "tier_1": {
                    "mydata": "mydata_Test_species.m",
                    "pars_init": "pars_init_Test_species.m",
                    "predict": "predict_Test_species.m",
                    "run": "run_Test_species.m",
                    "unknown": "extra_Test_species.m",
                }
            },
            tier_names=["tier_1"],
        )


def test_normalize_estimation_templates_rejects_non_matlab_template_strings():
    with pytest.raises(TypeError, match="MATLAB '.m' file paths"):
        normalize_estimation_templates(
            estimation_templates={
                "tier_1": {
                    "mydata": "mydata template",
                    "pars_init": "pars_init_Test_species.m",
                    "predict": "predict_Test_species.m",
                    "run": "run_Test_species.m",
                }
            },
            tier_names=["tier_1"],
        )


def test_build_estimation_templates_from_folder_returns_template_objects(tmp_path):
    species_name = "Test_species"
    _write_tier_template_folder(tmp_path, "tier_1", species_name)

    estimation_templates = build_estimation_templates_from_folder(
        template_folder=tmp_path,
        tier_names=["tier_1"],
        species_name=species_name,
    )

    assert isinstance(estimation_templates["tier_1"].mydata, MultitierMyDataSubstitutionTemplate)


def test_build_estimation_files_from_folder_warns_and_returns_estimation_templates(tmp_path):
    species_name = "Test_species"
    _write_tier_template_folder(tmp_path, "tier_1", species_name)

    with pytest.warns(
        DeprecationWarning,
        match="build_estimation_templates_from_folder\\(\\) is deprecated and will be removed in version 0\\.4\\.0",
    ):
        estimation_templates = build_estimation_templates_from_folder(
            template_folder=tmp_path,
            tier_names=["tier_1"],
            species_name=species_name,
        )

    assert isinstance(estimation_templates["tier_1"], EstimationTemplates)


def test_multitier_structure_coerces_matlab_path_strings_to_copy_templates(tmp_path):
    species_name = "Test_species"
    hierarchy = TierHierarchy(tier_names=["tier_1"], entities={"tier_1": ["entity_1"]})
    data = {"tier_1": FakeTierData()}
    output_folder = tmp_path / "outputs"

    multitier = MultiTierStructure(
        species_name=species_name,
        entity_hierarchy=hierarchy,
        data=data,
        pars={"par_a": 1.0},
        tier_pars={"tier_1": ["par_a"]},
        estimation_templates={
            "tier_1": {
                "mydata": str(tmp_path / "mydata_Test_species.m"),
                "pars_init": str(tmp_path / "pars_init_Test_species.m"),
                "predict": str(tmp_path / "predict_Test_species.m"),
                "run": str(tmp_path / "run_Test_species.m"),
            }
        },
        output_folder=output_folder,
        matlab_session="ignore",
    )

    assert isinstance(multitier.estimation_templates["tier_1"].mydata, CopyFileTemplate)
    assert isinstance(multitier.estimation_templates["tier_1"].predict, CopyFileTemplate)
    assert isinstance(multitier.tiers["tier_1"].estimation_templates.run, CopyFileTemplate)


def test_template_folder_deprecation_warning_and_internal_conversion(tmp_path):
    species_name = "Test_species"
    _write_tier_template_folder(tmp_path, "tier_1", species_name)
    hierarchy = TierHierarchy(tier_names=["tier_1"], entities={"tier_1": ["entity_1"]})
    data = {"tier_1": FakeTierData()}

    with pytest.warns(DeprecationWarning, match="template_folder"):
        multitier = MultiTierStructure(
            species_name=species_name,
            entity_hierarchy=hierarchy,
            data=data,
            pars={"par_a": 1.0},
            tier_pars={"tier_1": ["par_a"]},
            template_folder=tmp_path,
            output_folder=tmp_path / "outputs",
            matlab_session="ignore",
        )

    assert isinstance(multitier.estimation_templates["tier_1"].mydata, MultitierMyDataSubstitutionTemplate)
    assert isinstance(multitier.tiers["tier_1"].estimation_templates.mydata, MultitierMyDataSubstitutionTemplate)



def test_multitier_generic_templates_are_packaged_as_resources():
    contents = (
        resources.files("DEBtoolPyIF.multitier.resources.generic")
        .joinpath("mydata_template.m")
        .read_text(encoding="utf-8")
    )

    assert "$entity_data_block" in contents
    assert "$packing_block" in contents


def _build_multitier_context(tmp_path, tier_name="top", entity_list=None):
    tier_structure = FakeCodegenTierStructure()
    if entity_list is None:
        entity_list = ["root_entity"] if tier_name == "top" else ["child_a"]
    tier_estimator = SimpleNamespace(
        name=tier_name,
        tier_structure=tier_structure,
        tier_pars=["par_a"],
        extra_info="metaData.extra_info = NaN;",
        output_folder=tmp_path,
        estimation_settings={},
    )
    context = MultitierGenerationContext.from_tier_estimator(
        tier_estimator=tier_estimator,
        entity_list=entity_list,
        pseudo_data_weight=0.25,
        output_folder=tmp_path,
    )
    return context


def _replace_mydata_section(sections, *, key: str, content: str):
    return tuple(
        InlineMyDataSection(key=key, content=content) if section.key == key else section
        for section in sections
    )


def _replace_pars_init_section(sections, *, key: str, content: str):
    return tuple(
        InlineParsInitSection(key=key, content=content)
        if section.key == key
        else section
        for section in sections
    )


def _pars_init_registry_with(*definitions):
    parameter_registry = StdParameterRegistry()
    for definition in definitions:
        parameter_registry.add(definition)
    return parameter_registry


def _replace_run_section(sections, *, key: str, content: str):
    return tuple(
        InlineRunSection(key=key, content=content)
        if section.key == key
        else section
        for section in sections
    )


def test_mydata_template_renders_generated_sections(tmp_path):
    context = _build_multitier_context(tmp_path, tier_name="bottom", entity_list=["child_a"])
    sections = MultitierMyDataProgrammaticTemplate.required_sections() + (
        GroupDataTypesSection(),
        ExtraInfoSection(),
    )
    contents = MultitierMyDataProgrammaticTemplate(sections=sections).render(context)

    assert "metaData.group_data_types = {'group_a', 'group_m'};" in contents
    assert "% entity data" in contents
    assert "metaData.extra_info = NaN;" in contents
    assert "[data, units, label, weights] = addpseudodata(data, units, label, weights);" in contents
    assert "weights.psd.(varname) = 0.25;" in contents


def test_mydata_template_supports_custom_sections():
    context = SimpleNamespace(species_name="Test_species")
    template = MyDataProgrammaticTemplate(
        sections=(
            InlineMyDataSection(key="function_header", content="function test"),
            InlineMyDataSection(key="metadata_block", content="custom metadata"),
            InlineMyDataSection(key="typical_temperature_block", content="metaData.T_typical = 300;"),
            InlineMyDataSection(key="completeness_level_block", content="metaData.COMPLETE = 2.5;"),
            InlineMyDataSection(key="group_data_block", content="% group data"),
            InlineMyDataSection(key="entity_data_block", content="% data"),
            InlineMyDataSection(key="weights_block", content="weights = setweights(data, []);"),
            InlineMyDataSection(key="save_fields_block", content="metaData.data_fields = fieldnames(data);"),
            InlineMyDataSection(key="remove_dummy_weights_block", content="% remove dummy"),
            InlineMyDataSection(key="add_pseudodata_block", content="% add pseudo"),
            InlineMyDataSection(key="packing_block", content="end"),
        ),
    )

    assert "custom metadata" in template.render(context)

def test_build_mydata_substitutions_calls_state_builder_once():
    class CountingSection(MyDataSection):
        def __init__(self, key):
            self.key = key

        def render(self, _context, state: BaseMyDataState) -> str:
            return f"{self.key}:{len(state.entity_data_types)}"

    context = SimpleNamespace(species_name="Test_species")
    substitutions = build_mydata_substitutions(
        context,
        sections=(CountingSection("entity_data_block"), CountingSection("group_data_block")),
        state=BaseMyDataState(entity_data_types=("alpha", "beta")),
    )
    assert substitutions["entity_data_block"] == "entity_data_block:2"
    assert substitutions["group_data_block"] == "group_data_block:2"


def test_estimation_file_section_binds_init_substitutions_once():
    class BoundSection(EstimationFileSection):
        slot_name = "header"
        matlab_code = "${prefix}${species_name}"

        def __init__(self, prefix):
            self.prefix = prefix
            self.init_calls = 0
            super().__init__()

        def get_init_substitutions(self) -> dict[str, str]:
            self.init_calls += 1
            return {"prefix": self.prefix}

        def get_render_substitutions(self, context) -> dict[str, str]:
            return {"species_name": context.species_name}

    section = BoundSection("pars_init_")

    assert section.render(SimpleNamespace(species_name="first")) == "pars_init_first"
    assert section.render(SimpleNamespace(species_name="second")) == "pars_init_second"
    assert section.init_calls == 1


def test_mydata_function_header_uses_species_name_from_context():
    section = MyDataFunctionHeader()

    rendered = section.render(SimpleNamespace(species_name="Test_species"), BaseMyDataState())

    assert rendered.startswith(
        "function [data, auxData, metaData, txtData, weights] = mydata_Test_species"
    )


def test_mydata_function_header_can_bind_species_name_at_initialization():
    section = MyDataFunctionHeader(species_name="Bound_species")

    rendered = section.render(SimpleNamespace(species_name="Other_species"), BaseMyDataState())

    assert rendered.startswith(
        "function [data, auxData, metaData, txtData, weights] = mydata_Bound_species"
    )


def test_pars_init_function_header_can_bind_species_name_at_initialization():
    section = ParsInitFunctionHeader(species_name="Bound_species")

    rendered = section.render(SimpleNamespace(species_name="Other_species"))

    assert rendered == "function [par, metaPar, txtPar] = pars_init_Bound_species(metaData)"


def test_metadata_section_accepts_constructor_configuration():
    section = SpeciesInfoMetadataSection(
        species="Danio rerio",
        species_en="zebrafish",
    )

    rendered = section.render(SimpleNamespace(species_name="ignored"), BaseMyDataState())

    assert "metaData.species = 'Danio rerio';" in rendered
    assert "metaData.species_en = 'zebrafish';" in rendered
    assert "metaData.T_typical" not in rendered
    assert "metaData.COMPLETE" not in rendered
    assert rendered == section.render(SimpleNamespace(species_name="other"), BaseMyDataState())


def test_typical_temperature_section_renders_metadata_line():
    section = TypicalTemperatureSection(t_typical=310.15)

    rendered = section.render(SimpleNamespace(species_name="ignored"), BaseMyDataState())

    assert "metaData.T_typical = 310.15; % K, body temperature" in rendered


def test_typical_temperature_section_can_wrap_celsius_in_c2k():
    section = TypicalTemperatureSection(t_typical=38.6, is_celsius=True)

    rendered = section.render(SimpleNamespace(species_name="ignored"), BaseMyDataState())

    assert "metaData.T_typical = C2K(38.6); % K, body temperature" in rendered


def test_completeness_level_section_renders_metadata_line():
    section = CompletenessLevelSection(complete=3.1)

    rendered = section.render(SimpleNamespace(species_name="ignored"), BaseMyDataState())

    assert "metaData.COMPLETE = 3.1; % using criteria of LikaKear2011" in rendered


def test_author_info_metadata_section_uses_codegen_format():
    section = AuthorInfoMetadataSection(
        author=["Jane Doe", "John Doe"],
        email=("jane@example.com", "john@example.com"),
        address=("Lisbon", "Portugal"),
    )

    rendered = section.render(SimpleNamespace(species_name="ignored"), BaseMyDataState())

    assert "metaData.author = {'Jane Doe', 'John Doe'};" in rendered
    assert "metaData.email = {'jane@example.com', 'john@example.com'};" in rendered
    assert "metaData.address = {'Lisbon', 'Portugal'};" in rendered
    assert rendered == section.render(SimpleNamespace(species_name="other"), BaseMyDataState())


def test_packing_section_accepts_custom_field_lists():
    section = PackingSection(
        aux_data_fields=("temp", "custom_aux"),
        txt_data_fields=("units", "custom_txt"),
    )

    rendered = section.render(SimpleNamespace(species_name="ignored"), BaseMyDataState())

    assert "auxData.temp = temp;" in rendered
    assert "auxData.custom_aux = custom_aux;" in rendered
    assert "txtData.units = units;" in rendered
    assert "txtData.custom_txt = custom_txt;" in rendered
    assert rendered.endswith("end")


def test_mydata_source_template_preserves_unsupported_template_keys(tmp_path):
    context = _build_multitier_context(tmp_path)

    assert MyDataSubstitutionTemplate(source="$unsupported_key").render(context) == "$unsupported_key"


def test_mydata_source_template_allows_partial_placeholder_sets(tmp_path):
    context = _build_multitier_context(tmp_path)

    assert MyDataSubstitutionTemplate(source="$function_header").render(context).startswith(
        "function [data, auxData, metaData, txtData, weights] = mydata_Test_species"
    )


def test_mydata_source_template_renders_entity_iteration_sections_to_info():
    context = SimpleNamespace(
        species_name="Test_species",
        entity_list=("entity_1", "entity_2"),
        groups_of_entity={
            "entity_1": ["group_a"],
            "entity_2": ["group_a", "group_b"],
        },
    )
    source = "\n".join(["$entity_list", "$groups_of_entity"])

    contents = MyDataSubstitutionTemplate(source=source).render(context)

    assert "info.entity_list = {'entity_1', 'entity_2'};" in contents
    assert "info.groups_of_entity = struct(" in contents
    assert "'entity_1', {{'group_a'}}" in contents
    assert "'entity_2', {{'group_a', 'group_b'}}" in contents
    assert "tiers.entity_list" not in contents
    assert "metaData.entity_list" not in contents


def test_mydata_template_preserves_required_defaults_when_user_sections_are_partial(tmp_path):
    with pytest.raises(ValueError, match="Missing required mydata sections"):
        MyDataProgrammaticTemplate(
            sections=(
                InlineMyDataSection(key="function_header", content="function custom"),
                InlineMyDataSection(key="metadata_block", content="meta custom"),
            ),
        )


def test_mydata_template_rejects_duplicate_section_keys():
    with pytest.raises(ValueError, match="Duplicate mydata section key 'function_header'"):
        MyDataProgrammaticTemplate(
            sections=(
                InlineMyDataSection(key="function_header", content="function one"),
                InlineMyDataSection(key="function_header", content="function two"),
                InlineMyDataSection(key="metadata_block", content="meta"),
                InlineMyDataSection(key="group_data_block", content="% group"),
                InlineMyDataSection(key="entity_data_block", content="% entity"),
                InlineMyDataSection(key="weights_block", content="weights = setweights(data, []);"),
                InlineMyDataSection(key="save_fields_block", content="metaData.data_fields = fieldnames(data);"),
                InlineMyDataSection(key="remove_dummy_weights_block", content="% remove dummy"),
                InlineMyDataSection(key="add_pseudodata_block", content="% add pseudo"),
                InlineMyDataSection(key="packing_block", content="end"),
            ),
        )


def test_mydata_template_uses_minimum_required_blocks_by_default(tmp_path):
    context = _build_multitier_context(tmp_path, tier_name="top", entity_list=["root_entity"])

    contents = MyDataProgrammaticTemplate().render(context)

    assert "weights = setweights(data, []);" in contents
    assert "metaData.data_fields = fieldnames(data);" in contents
    assert "[data, units, label, weights] = addpseudodata(data, units, label, weights);" in contents
    assert "metaData.group_data_types" not in contents


def test_mydata_template_required_sections_returns_complete_valid_base_tuple():
    template = MyDataProgrammaticTemplate(sections=MyDataProgrammaticTemplate.required_sections())

    assert tuple(section.key for section in template.get_sections()) == (
        "function_header",
        "metadata_block",
        "typical_temperature_block",
        "completeness_level_block",
        "group_data_block",
        "entity_data_block",
        "weights_block",
        "save_fields_block",
        "remove_dummy_weights_block",
        "add_pseudodata_block",
        "packing_block",
    )


def test_mydata_template_data_sections_helper_returns_data_sections():
    assert tuple(section.key for section in MyDataProgrammaticTemplate.data_sections()) == (
        "group_data_block",
        "group_data_types",
        "entity_data_block",
        "entity_data_types",
        "entity_list",
        "groups_of_entity",
    )
    assert tuple(type(section) for section in MyDataTemplate.data_sections()) == (
        GroupDataSection,
        GroupDataTypesSection,
        EntityDataSection,
        EntityDataTypesSection,
        EntityListSection,
        GroupsOfEntitySection,
    )


def test_mydata_section_opt_in_registration_updates_allowed_keys_automatically():
    class AutoRegisteredSection(MyDataSection):
        key = "auto_registered_test_block"
        template_families = ("mydata",)
        section_tags = ("metadata",)

    assert "auto_registered_test_block" in MyDataTemplate.allowed_section_keys()
    assert "auto_registered_test_block" in MultitierMyDataTemplate.allowed_section_keys()
    assert AutoRegisteredSection in MyDataTemplate.available_section_classes()


def test_mydata_section_without_opt_in_registration_is_not_allowed():
    class UnregisteredSection(MyDataSection):
        key = "unregistered_test_block"

    assert "unregistered_test_block" not in MyDataTemplate.allowed_section_keys()
    assert UnregisteredSection not in MyDataTemplate.available_section_classes()


def test_mydata_section_inherited_template_families_do_not_register_subclass():
    class ParentRegisteredSection(MyDataSection):
        key = "parent_inherited_registration_test_block"
        template_families = ("mydata",)

    class ChildWithoutDirectFamilies(ParentRegisteredSection):
        key = "child_inherited_registration_test_block"

    assert "parent_inherited_registration_test_block" in MyDataTemplate.allowed_section_keys()
    assert "child_inherited_registration_test_block" not in MyDataTemplate.allowed_section_keys()
    assert ChildWithoutDirectFamilies not in MyDataTemplate.available_section_classes()


def test_mydata_section_duplicate_registration_raises_immediately():
    class FirstRegisteredSection(MyDataSection):
        key = "duplicate_registration_test_block"
        template_families = ("mydata",)

    with pytest.raises(ValueError, match="Duplicate mydata section key 'duplicate_registration_test_block'"):
        class DuplicateRegisteredSection(MyDataSection):
            key = "duplicate_registration_test_block"
            template_families = ("mydata",)


def test_mydata_template_replaces_default_block_by_key(tmp_path):
    context = _build_multitier_context(tmp_path, tier_name="top", entity_list=["root_entity"])
    template = MyDataProgrammaticTemplate(sections=_replace_mydata_section(
        MyDataProgrammaticTemplate.required_sections(),
        key="metadata_block",
        content="custom metadata block",
    ))

    contents = template.render(context)

    assert "custom metadata block" in contents


def test_mydata_template_uses_only_user_provided_sections(tmp_path):
    context = _build_multitier_context(tmp_path, tier_name="top", entity_list=["root_entity"])
    sections = MyDataProgrammaticTemplate.required_sections() + (
        InlineMyDataSection(key="discussion_block", content="custom discussion"),
    )

    contents = MyDataProgrammaticTemplate(sections=sections).render(context)

    assert "custom discussion" in contents
    assert "%% Set temperature metadata" not in contents


def test_multitier_mydata_template_uses_minimum_required_multitier_blocks(tmp_path):
    context = _build_multitier_context(tmp_path, tier_name="bottom", entity_list=["child_a"])

    contents = MultitierMyDataProgrammaticTemplate().render(context)

    assert "weights.psd.(varname) = 0.25;" in contents
    assert "auxData.tiers = tiers;" in contents


def test_multitier_mydata_template_required_sections_returns_complete_valid_tuple():
    template = MultitierMyDataProgrammaticTemplate(
        sections=MultitierMyDataProgrammaticTemplate.required_sections()
    )

    assert tuple(section.key for section in template.get_sections()) == (
        "function_header",
        "metadata_block",
        "typical_temperature_block",
        "completeness_level_block",
        "group_data_block",
        "entity_data_block",
        "entity_list",
        "tier_entities",
        "tier_groups",
        "groups_of_entity",
        "tier_subtree",
        "tier_pars",
        "tier_par_init_values",
        "weights_block",
        "save_fields_block",
        "remove_dummy_weights_block",
        "add_pseudodata_block",
        "multitier_pseudodata_block",
        "packing_block",
    )


def test_multitier_mydata_template_tier_variable_sections_helper_returns_tier_sections():
    assert tuple(section.key for section in MultitierMyDataProgrammaticTemplate.tier_variable_sections()) == (
        "entity_list",
        "tier_entities",
        "tier_groups",
        "groups_of_entity",
        "tier_subtree",
        "tier_pars",
        "tier_par_init_values",
    )
    assert tuple(type(section) for section in MultitierMyDataTemplate.tier_variable_sections()) == (
        MultitierEntityListSection,
        TierEntitiesSection,
        TierGroupsSection,
        MultitierGroupsOfEntitySection,
        TierSubtreeSection,
        TierParsSection,
        TierParInitValuesSection,
    )


def test_mydata_template_allowed_section_keys_include_registered_metadata_sections():
    allowed_keys = MyDataTemplate.allowed_section_keys()

    assert "author_info_block" in allowed_keys
    assert "typical_temperature_block" in allowed_keys
    assert "completeness_level_block" in allowed_keys


def test_multitier_mydata_template_allowed_section_keys_include_multitier_sections():
    allowed_keys = MultitierMyDataTemplate.allowed_section_keys()

    assert "set_temperature_equal_to_typical_block" in allowed_keys
    assert "multitier_pseudodata_block" in allowed_keys


def test_multitier_mydata_template_uses_specialized_classes_for_duplicate_generic_keys():
    assert type(MultitierMyDataProgrammaticTemplate.required_sections()[-1]).__name__ == "MultitierPackingSection"


def test_multitier_mydata_template_rejects_missing_required_sections():
    with pytest.raises(ValueError, match="Missing required mydata sections"):
        MultitierMyDataProgrammaticTemplate(sections=MyDataProgrammaticTemplate.required_sections())


def test_mydata_source_template_returns_plain_source_when_no_placeholders():
    context = SimpleNamespace(species_name="Test_species")

    assert MyDataSubstitutionTemplate(source="% plain template").render(context) == "% plain template"


def test_mydata_copy_file_template_returns_source_unchanged(tmp_path):
    path = tmp_path / "mydata_Test_species.m"
    path.write_text("% handwritten mydata\n", encoding="utf-8")
    context = SimpleNamespace(species_name="Test_species")

    assert CopyFileTemplate(path).render(context) == "% handwritten mydata\n"


def test_multitier_pseudodata_block_is_empty_for_root_tier(tmp_path):
    tier_structure = FakeCodegenTierStructure()
    tier_estimator = SimpleNamespace(
        name="top",
        tier_structure=tier_structure,
        tier_pars=["par_a"],
        extra_info="",
        output_folder=tmp_path,
        estimation_settings={},
    )
    context = MultitierGenerationContext.from_tier_estimator(
        tier_estimator=tier_estimator,
        entity_list=["root_entity"],
        pseudo_data_weight=0.25,
        output_folder=tmp_path,
    )
    source = "\n".join(
        [
            "$function_header",
            "$metadata_block",
            "$group_data_block",
            "$entity_data_block",
            "$entity_list",
            "$tier_entities",
            "$tier_groups",
            "$groups_of_entity",
            "$tier_subtree",
            "$tier_pars",
            "$tier_par_init_values",
            "$weights_block",
            "$save_fields_block",
            "$remove_dummy_weights_block",
            "$add_pseudodata_block",
            "$multitier_pseudodata_block",
            "$packing_block",
        ]
    )

    contents = MultitierMyDataSubstitutionTemplate(source=source).render(context)

    assert "[data, units, label, weights] = addpseudodata(data, units, label, weights);" in contents
    assert "weights.psd.(varname)" not in contents


def test_multitier_packing_adds_tiers_to_auxdata(tmp_path):
    context = _build_multitier_context(tmp_path, tier_name="bottom", entity_list=["child_a"])
    source = "\n".join(
        [
            "$function_header",
            "$metadata_block",
            "$group_data_block",
            "$entity_data_block",
            "$entity_list",
            "$tier_entities",
            "$tier_groups",
            "$groups_of_entity",
            "$tier_subtree",
            "$tier_pars",
            "$tier_par_init_values",
            "$weights_block",
            "$save_fields_block",
            "$remove_dummy_weights_block",
            "$add_pseudodata_block",
            "$multitier_pseudodata_block",
            "$packing_block",
        ]
    )

    contents = MultitierMyDataSubstitutionTemplate(source=source).render(context)

    assert "auxData.tiers = tiers;" in contents


def test_multitier_entity_iteration_sections_still_render_to_tiers(tmp_path):
    context = _build_multitier_context(tmp_path, tier_name="bottom", entity_list=["child_a"])
    source = "\n".join(["$entity_list", "$groups_of_entity"])

    contents = MultitierMyDataSubstitutionTemplate(source=source).render(context)

    assert "tiers.entity_list = {'child_a'};" in contents
    assert "metaData.entity_list = tiers.entity_list;" in contents
    assert "tiers.groups_of_entity = struct('child_a', {{}});" in contents
    assert "info.entity_list" not in contents
    assert "info.groups_of_entity" not in contents


def test_pars_init_template_renders_builtins_and_expansion():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"p_Am": 12.5, "kap_X": 0.25, "del_M": 0.15},
        tier_pars=["p_Am"],
        get_file_sections=lambda file_key: (),
    )

    tier_loop_context = SimpleNamespace(
        species_name=context.species_name,
        full_pars_dict=context.full_pars_dict,
        tier_pars=context.tier_pars,
        tier_name="top",
        entity_list=["entity_1"],
        tier_par_init_values={"p_Am": {"entity_1": 1.0}},
    )
    parameter_registry = _pars_init_registry_with(p_Am, del_M)
    contents = MultitierParsInitProgrammaticTemplate(
        sections=_replace_pars_init_section(
            build_registry_multitier_pars_init_sections(parameter_registry=parameter_registry),
            key="tier_parameter_loops",
            content="loop block",
        ),
    ).render(tier_loop_context)

    assert "function [par, metaPar, txtPar] = pars_init_Test_species(metaData)" in contents
    assert "par.p_Am = 12.5;" in contents
    assert "par.T_ref = 293.15;" in contents
    assert "loop block" in contents


def test_pars_init_template_required_sections_returns_complete_valid_tuple():
    template = ParsInitProgrammaticTemplate(sections=ParsInitProgrammaticTemplate.required_sections())

    assert tuple(section.key for section in template.get_sections()) == (
        "function_header",
        "model_metadata",
        "reference_temperature",
        "base_parameters",
        "addchem",
        "packing",
    )


def test_multitier_pars_init_template_required_sections_returns_complete_valid_tuple():
    template = MultitierParsInitProgrammaticTemplate(
        sections=MultitierParsInitProgrammaticTemplate.required_sections()
    )

    assert tuple(section.key for section in template.get_sections()) == (
        "function_header",
        "model_metadata",
        "reference_temperature",
        "base_parameters",
        "addchem",
        "tier_parameter_loops",
        "packing",
    )


def test_pars_init_template_uses_only_user_provided_sections():
    sections = _replace_pars_init_section(
        build_registry_multitier_pars_init_sections(
            parameter_registry=_pars_init_registry_with(p_Am),
        ),
        key="tier_parameter_loops",
        content="custom optional block",
    )
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"p_Am": 12.5},
        tier_pars=["p_Am"],
        tier_name="top",
        entity_list=["entity_1"],
        tier_par_init_values={"p_Am": {"entity_1": 1.0}},
    )

    contents = MultitierParsInitProgrammaticTemplate(sections=sections).render(context)

    assert "custom optional block" in contents


def test_pars_init_source_template_uses_source_path_independently():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"p_Am": 12.5, "kap_X": 0.25, "del_M": 0.15},
        tier_pars=["p_Am"],
        tier_name="top",
        entity_list=["entity_1"],
        tier_par_init_values={"p_Am": {"entity_1": 1.0}},
    )
    source = "\n".join(
        [
            "$function_header",
            "$model_metadata",
            "$base_parameters",
            "$addchem",
            "$tier_parameter_loops",
            "$packing",
        ]
    )

    source_template_contents = RegistryMultitierParsInitSubstitutionTemplate(
        source=source,
        parameter_registry=_pars_init_registry_with(p_Am, del_M),
    ).render(context)

    assert "function [par, metaPar, txtPar] = pars_init_Test_species(metaData)" in source_template_contents
    assert "par.p_Am = 12.5;" in source_template_contents


def test_pars_init_source_template_allows_partial_placeholder_sets():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"p_Am": 12.5},
        tier_pars=["p_Am"],
        tier_name="top",
        entity_list=["entity_1"],
        tier_par_init_values={"p_Am": {"entity_1": 1.0}},
    )

    assert MultitierParsInitSubstitutionTemplate(source="$function_header").render(context).startswith(
        "function [par, metaPar, txtPar] = pars_init_Test_species(metaData)"
    )


def test_pars_init_chemical_parameters_section_renders_only_supplied_properties():
    section = ParsInitChemicalParametersSection(
        chemical_parameter_values=(
            ChemicalParameterValues.from_compound(
                compound_symbol="N",
                compound_name="n-waste",
                mu=518181,
                n_C=1,
                n_H=2.216,
            ),
        )
    )

    rendered = section.render(SimpleNamespace())

    assert "par.mu_N = 518181;" in rendered
    assert "free.mu_N = 0;" in rendered
    assert "units.mu_N = 'J/ mol';" in rendered
    assert "label.mu_N = 'chem. potential of n-waste';" in rendered
    assert "par.n_CN = 1;" in rendered
    assert "free.n_CN = 0;" in rendered
    assert "par.n_HN = 2.216;" in rendered
    assert "free.n_HN = 0;" in rendered
    assert "par.n_ON" not in rendered
    assert "par.n_NN" not in rendered


def test_pars_init_chemical_parameters_section_renders_empty_string_without_overrides():
    assert ParsInitChemicalParametersSection().render(SimpleNamespace()) == ""


def test_pars_init_chemical_parameters_section_rejects_non_value_entries():
    with pytest.raises(TypeError, match="ChemicalParameterValues instances"):
        ParsInitChemicalParametersSection(chemical_parameter_values=("bad",))


def test_pars_init_chemical_parameters_section_is_auto_registered():
    assert "chemical_parameters" in ParsInitTemplate.allowed_section_keys()


def test_pars_init_reference_temperature_section_renders_default_kelvin_value():
    rendered = ParsInitReferenceTemperatureSection().render(SimpleNamespace())

    assert rendered == (
        "par.T_ref = 293.15; free.T_ref = 0; units.T_ref = 'K'; "
        "label.T_ref = 'Reference temperature';"
    )


def test_pars_init_reference_temperature_section_converts_celsius_at_construction_time():
    section = ParsInitReferenceTemperatureSection(t_ref=20, is_celsius=True)

    rendered = section.render(SimpleNamespace(unused_value="ignored"))

    assert rendered == (
        "par.T_ref = C2K(20); free.T_ref = 0; units.T_ref = 'K'; "
        "label.T_ref = 'Reference temperature';"
    )


def test_pars_init_template_accepts_explicit_chemical_parameters_section():
    template = ParsInitProgrammaticTemplate(
        sections=(
            InlineParsInitSection(key="function_header", content="function test"),
            InlineParsInitSection(key="model_metadata", content="metaPar.model = 'std';"),
            InlineParsInitSection(
                key="reference_temperature",
                content="par.T_ref = 293.15; free.T_ref = 0; units.T_ref = 'K'; label.T_ref = 'Reference temperature';",
            ),
            InlineParsInitSection(key="base_parameters", content=""),
            InlineParsInitSection(key="addchem", content="[par, units, label, free] = addchem(...);"),
            ParsInitChemicalParametersSection(
                chemical_parameter_values=(
                    ChemicalParameterValues.from_compound(
                        compound_symbol="N",
                        compound_name="n-waste",
                        n_N=0.897,
                    ),
                )
            ),
            InlineParsInitSection(key="packing", content="end"),
        )
    )

    rendered = template.render(SimpleNamespace())

    assert "par.n_NN = 0.897;" in rendered
    assert "free.n_NN = 0;" in rendered


def test_pars_init_source_template_accepts_explicit_chemical_parameters_section():
    template = ParsInitSubstitutionTemplate(
        source="$function_header\n$addchem\n$chemical_parameters\n$packing",
        sections=(
            ParsInitFunctionHeader(species_name="Test_species"),
            ParsInitAddChemSection(),
            ParsInitChemicalParametersSection(
                chemical_parameter_values=(
                    ChemicalParameterValues.from_compound(
                        compound_symbol="N",
                        compound_name="n-waste",
                        n_O=0.594,
                    ),
                )
            ),
            InlineParsInitSection(key="packing", content="end"),
        ),
    )

    rendered = template.render(SimpleNamespace(species_name="Ignored"))

    assert "function [par, metaPar, txtPar] = pars_init_Test_species(metaData)" in rendered
    assert "par.n_ON = 0.594;" in rendered


def test_pars_init_template_rejects_missing_required_sections():
    with pytest.raises(ValueError, match="Missing required pars_init sections"):
        ParsInitProgrammaticTemplate(sections=(InlineParsInitSection(key="function_header", content="header"),))


def test_pars_init_template_rejects_legacy_slot_sections():
    with pytest.raises(TypeError, match="ParsInitSection instances"):
        ParsInitProgrammaticTemplate(
            sections=(
                InlineEstimationSection(slot_name="function_header", content="header"),
            ),
        )


def test_pars_init_programmatic_template_is_section_only():
    with pytest.raises(TypeError):
        ParsInitProgrammaticTemplate(custom_parameters=())


def test_parameter_definitions_are_public_reusable_objects():
    from DEBtoolPyIF.parameters.definitions import ParameterDefinition as DefinitionParameterDefinition

    assert DefinitionParameterDefinition is ParameterDefinition
    assert p_Am.name == "p_Am"
    assert get_parameter_definition("p_Am") is p_Am
    assert require_parameter_definition("del_M") is del_M
    assert get_parameter_definition("E_Hx") is E_Hx
    assert get_parameter_definition("p_Am_f") is None


def test_parameter_definition_catalog_views_stay_in_sync():
    all_names = tuple(definition.name for definition in ALL_PARAMETER_DEFINITIONS)

    assert all_names == tuple(PARAMETER_DEFINITIONS_BY_NAME.keys())
    assert all(PARAMETER_DEFINITIONS_BY_NAME[name] is definition for name, definition in zip(all_names, ALL_PARAMETER_DEFINITIONS))
    assert tuple(definition.name for definition in DEFAULT_PARAMETER_DEFINITIONS) == (
        "T_A",
        "z",
        "F_m",
        "kap_X",
        "kap_P",
        "v",
        "kap",
        "p_M",
        "p_T",
        "k_J",
        "E_G",
        "E_Hb",
        "E_Hp",
        "kap_R",
        "h_a",
        "s_G",
        "f",
    )


def test_parameter_definitions_module_all_exports_all_registered_builtins():
    builtin_names = tuple(definition.name for definition in ALL_PARAMETER_DEFINITIONS)

    assert "ParameterDefinition" in parameter_definitions_module.__all__
    assert "get_parameter_definition" in parameter_definitions_module.__all__
    assert "require_parameter_definition" in parameter_definitions_module.__all__
    assert tuple(
        name for name in parameter_definitions_module.__all__
        if name in PARAMETER_DEFINITIONS_BY_NAME
    ) == builtin_names


def test_parameters_package_all_excludes_individual_builtin_definition_names():
    builtin_names = set(PARAMETER_DEFINITIONS_BY_NAME)

    assert "ParameterDefinition" in parameters_package.__all__
    assert "ParameterRegistry" in parameters_package.__all__
    assert "get_parameter_registry_of_typified_model" in parameters_package.__all__
    assert "StdParameterRegistry" in parameters_package.__all__
    assert "StxParameterRegistry" in parameters_package.__all__
    assert "get_parameter_definition" in parameters_package.__all__
    assert "require_parameter_definition" in parameters_package.__all__
    assert "ChemicalParameters" in parameters_package.__all__
    assert "get_chemical_parameter_values_of" in parameters_package.__all__
    assert "get_chemical_parameters_of" in parameters_package.__all__
    assert builtin_names.isdisjoint(parameters_package.__all__)


def test_chemical_parameter_definition_classes_derive_metadata_from_compound():
    mu = ChemicalPotentialDefinition("N", "n-waste", default_value=518181)
    n_c = CarbonChemicalIndexDefinition("N", "n-waste")
    n_h = HydrogenChemicalIndexDefinition("N", "n-waste", default_value=2.216)
    n_o = OxygenChemicalIndexDefinition("N", "n-waste", default_value=0.594)
    n_n = NitrogenChemicalIndexDefinition("N", "n-waste", default_value=0.897)

    assert isinstance(mu, ParameterDefinition)
    assert isinstance(n_c, ParameterDefinition)
    assert isinstance(n_h, ParameterDefinition)
    assert isinstance(n_o, ParameterDefinition)
    assert isinstance(n_n, ParameterDefinition)
    assert (
        mu.name,
        mu.units,
        mu.label,
        mu.default_value,
        mu.default_free,
    ) == ("mu_N", "J/ mol", "chem. potential of n-waste", 518181, 0)
    assert (
        n_c.name,
        n_c.units,
        n_c.label,
        n_c.default_value,
        n_c.default_free,
    ) == ("n_CN", "-", "chem. index of carbon in n-waste", 1, 0)
    assert (
        n_h.name,
        n_h.units,
        n_h.label,
        n_h.default_value,
        n_h.default_free,
    ) == ("n_HN", "-", "chem. index of hydrogen in n-waste", 2.216, 0)
    assert (
        n_o.name,
        n_o.units,
        n_o.label,
        n_o.default_value,
        n_o.default_free,
    ) == ("n_ON", "-", "chem. index of oxygen in n-waste", 0.594, 0)
    assert (
        n_n.name,
        n_n.units,
        n_n.label,
        n_n.default_value,
        n_n.default_free,
    ) == ("n_NN", "-", "chem. index of nitrogen in n-waste", 0.897, 0)


def test_get_chemical_parameters_of_returns_grouped_chemical_parameters():
    chemical_parameters = get_chemical_parameters_of(" N ")

    assert isinstance(chemical_parameters, ChemicalParameters)
    assert chemical_parameters.compound_symbol == "N"
    assert chemical_parameters.compound_name == "n-waste"
    assert chemical_parameters.definitions == (
        chemical_parameters.mu,
        chemical_parameters.n_C,
        chemical_parameters.n_H,
        chemical_parameters.n_O,
        chemical_parameters.n_N,
    )
    assert tuple(definition.name for definition in chemical_parameters.as_tuple()) == (
        "mu_N",
        "n_CN",
        "n_HN",
        "n_ON",
        "n_NN",
    )
    assert chemical_parameters.n_C.default_value == 1


def test_get_chemical_parameters_of_accepts_standard_names_and_aliases():
    assert get_chemical_parameters_of("food").compound_symbol == "X"
    assert get_chemical_parameters_of("faeces").compound_symbol == "P"
    assert get_chemical_parameters_of("feces").compound_symbol == "P"
    assert get_chemical_parameters_of("carbon dioxide").compound_symbol == "C"


def test_get_chemical_parameters_of_rejects_unknown_compounds():
    with pytest.raises(ValueError, match="Unknown chemical compound 'bad'"):
        get_chemical_parameters_of("bad")


def test_get_chemical_parameter_values_of_returns_food_defaults():
    chemical_values = get_chemical_parameter_values_of("food")

    assert chemical_values.chemical_parameters.compound_symbol == "X"
    assert chemical_values.chemical_parameters.compound_name == "food"
    assert (
        chemical_values.mu,
        chemical_values.n_C,
        chemical_values.n_H,
        chemical_values.n_O,
        chemical_values.n_N,
    ) == (525000, 1, 1.8, 0.5, 0.15)


def test_get_chemical_parameter_values_of_returns_standard_gas_defaults():
    carbon_dioxide = get_chemical_parameter_values_of("carbon dioxide")
    water = get_chemical_parameter_values_of("water")
    oxygen = get_chemical_parameter_values_of("O")

    assert carbon_dioxide.chemical_parameters.compound_symbol == "C"
    assert (carbon_dioxide.mu, carbon_dioxide.n_C, carbon_dioxide.n_H, carbon_dioxide.n_O, carbon_dioxide.n_N) == (
        0,
        1,
        0,
        2,
        0,
    )
    assert water.chemical_parameters.compound_symbol == "H"
    assert (water.mu, water.n_C, water.n_H, water.n_O, water.n_N) == (0, 0, 2, 1, 0)
    assert oxygen.chemical_parameters.compound_symbol == "O"
    assert (oxygen.mu, oxygen.n_C, oxygen.n_H, oxygen.n_O, oxygen.n_N) == (0, 0, 0, 2, 0)


def test_get_chemical_parameter_values_of_returns_named_n_waste_variant_defaults():
    ammonia = get_chemical_parameter_values_of("ammonia")
    urea = get_chemical_parameter_values_of("urea")
    uric_acid = get_chemical_parameter_values_of("uric acid")

    assert ammonia.chemical_parameters.compound_symbol == "N"
    assert (ammonia.mu, ammonia.n_C, ammonia.n_H, ammonia.n_O, ammonia.n_N) == (339250, 0, 3, 0, 1)
    assert urea.chemical_parameters.compound_symbol == "N"
    assert (urea.mu, urea.n_C, urea.n_H, urea.n_O, urea.n_N) == (662200, 1, 4, 1, 2)
    assert uric_acid.chemical_parameters.compound_symbol == "N"
    assert (uric_acid.mu, uric_acid.n_C, uric_acid.n_H, uric_acid.n_O, uric_acid.n_N) == (
        417480,
        1,
        0.8,
        0.6,
        0.8,
    )


def test_get_chemical_parameter_values_of_returns_methane_defaults():
    methane = get_chemical_parameter_values_of("methane")

    assert methane.chemical_parameters.compound_symbol == "M"
    assert methane.chemical_parameters.compound_name == "methane"
    assert (methane.mu, methane.n_C, methane.n_H, methane.n_O, methane.n_N) == (816000, 1, 4, 0, 0)


def test_get_chemical_parameter_values_of_accepts_overrides():
    chemical_values = get_chemical_parameter_values_of("food", mu=530000, n_O=0.7)

    assert (chemical_values.mu, chemical_values.n_C, chemical_values.n_H, chemical_values.n_O, chemical_values.n_N) == (
        530000,
        1,
        1.8,
        0.7,
        0.15,
    )


def test_get_chemical_parameter_values_of_rejects_ambiguous_n_waste_defaults():
    with pytest.raises(ValueError, match="ambiguous"):
        get_chemical_parameter_values_of("N")
    with pytest.raises(ValueError, match="ambiguous"):
        get_chemical_parameter_values_of("n-waste")


def test_chemical_parameter_values_convenience_constructors_reduce_manual_wiring():
    common = ChemicalParameterValues.from_common_compound("methane", n_H=4.1)
    custom = ChemicalParameterValues.from_compound(
        compound_symbol="Q",
        compound_name="custom compound",
        mu=123,
        n_C=1,
        n_H=2,
        n_O=3,
        n_N=4,
    )

    assert common.chemical_parameters.compound_symbol == "M"
    assert (common.mu, common.n_C, common.n_H, common.n_O, common.n_N) == (816000, 1, 4.1, 0, 0)
    assert custom.chemical_parameters.compound_symbol == "Q"
    assert custom.chemical_parameters.compound_name == "custom compound"
    assert (custom.mu, custom.n_C, custom.n_H, custom.n_O, custom.n_N) == (123, 1, 2, 3, 4)


def test_parameter_definition_replace_preserves_unspecified_fields():
    original = p_Am

    derived = original.replace(
        name="p_Am_f",
        label="Surface-specific maximum assimilation rate for females",
    )

    assert derived is not original
    assert derived.name == "p_Am_f"
    assert derived.units == original.units
    assert derived.label == "Surface-specific maximum assimilation rate for females"
    assert derived.default_value == original.default_value
    assert derived.default_free == original.default_free
    assert derived.float_format == original.float_format
    assert derived.latex_label == original.latex_label
    assert original.name == "p_Am"
    assert original.label == "Surface-specific maximum assimilation rate"


def test_parameter_definition_replace_allows_overriding_optional_metadata():
    original = ParameterDefinition(
        name="kap_X",
        units="-",
        label="digestion efficiency of food to reserve",
        default_value=0.8,
        default_free=0,
        float_format="%.4f",
        latex_label="\\kappa_X",
    )

    derived = original.replace(
        default_value=None,
        default_free=1,
        float_format=None,
        latex_label="\\kappa_{X,f}",
    )

    assert derived == ParameterDefinition(
        name="kap_X",
        units="-",
        label="digestion efficiency of food to reserve",
        default_value=None,
        default_free=1,
        float_format=None,
        latex_label="\\kappa_{X,f}",
    )
    registry = ParameterRegistry([derived])
    assert registry.require("kap_X") is derived
    assert original.default_value == 0.8
    assert original.default_free == 0
    assert original.float_format == "%.4f"
    assert original.latex_label == "\\kappa_X"


def test_parameter_definition_clean_breaks_from_registry_module():
    assert not hasattr(parameter_registry_module, "ParameterDefinition")
    with pytest.raises(ImportError):
        from DEBtoolPyIF.parameters.registry import ParameterDefinition as RegistryParameterDefinition

        del RegistryParameterDefinition


def test_std_parameter_registry_uses_default_definitions_only():
    parameter_names = {definition.name for definition in DEFAULT_PARAMETER_DEFINITIONS}
    registry = StdParameterRegistry()

    assert "T_ref" not in parameter_names
    assert "kap_X" in parameter_names
    assert registry.get("T_ref") is None
    assert registry.get("kap_X").units == "-"
    for parameter_name in ("p_Am", "t_0", "E_Hx", "del_M", "p_Am_f", "E_Hp_f"):
        assert parameter_name not in parameter_names
        assert registry.get(parameter_name) is None


def test_stx_parameter_registry_extends_std_with_stx_specific_definitions():
    std_registry = StdParameterRegistry()
    stx_registry = StxParameterRegistry()

    for parameter_name in ("kap_X", "E_Hp"):
        assert stx_registry.require(parameter_name) is std_registry.require(parameter_name)
    assert std_registry.get("T_ref") is None
    assert stx_registry.get("T_ref") is None
    assert stx_registry.require("E_Hx") is E_Hx
    assert stx_registry.require("t_0") is t_0
    assert stx_registry.get("p_Am") is None
    assert stx_registry.get("del_M") is None


def test_angus_registry_adds_non_default_and_example_specific_definitions():
    from examples.Bos_taurus_Angus.templates import build_angus_parameter_registry

    registry = build_angus_parameter_registry()

    for parameter_name in ("p_Am", "t_0", "E_Hx", "del_M", "p_Am_f", "E_Hp_f"):
        assert registry.get(parameter_name) is not None


def test_registry_pars_init_template_defaults_to_std_model():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"kap_X": 0.25},
        tier_pars=[],
        get_file_sections=lambda file_key: (),
    )

    contents = RegistryParsInitProgrammaticTemplate().render(context)

    assert "metaPar.model = 'std';" in contents
    assert "par.T_ref = 293.15;" in contents


def test_registry_pars_init_template_uses_stx_registry_when_requested():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"E_Hx": 2.5},
        tier_pars=[],
        get_file_sections=lambda file_key: (),
    )

    contents = RegistryParsInitProgrammaticTemplate(model="stx").render(context)

    assert "metaPar.model = 'stx';" in contents
    assert "par.E_Hx = 2.5;" in contents


def test_registry_pars_init_template_requires_explicit_registry_for_nat_model():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"kap_X": 0.25},
        tier_pars=[],
        get_file_sections=lambda file_key: (),
    )

    with pytest.raises(ValueError, match="No built-in parameter registry is available for model 'nat'"):
        RegistryParsInitProgrammaticTemplate(model="nat").render(context)


def test_registry_pars_init_programmatic_template_extends_section_template():
    template = RegistryParsInitProgrammaticTemplate()

    assert isinstance(template, ParsInitProgrammaticTemplate)


def test_pars_init_section_registration_updates_allowed_keys_automatically():
    class AutoRegisteredParsInitSection(ParsInitSection):
        key = "auto_registered_pars_init_block"
        template_families = ("pars_init",)
        section_tags = ("metadata",)

    assert "auto_registered_pars_init_block" in ParsInitTemplate.allowed_section_keys()


def test_section_registries_are_isolated_for_pars_init_root():
    class MyDataRegisteredInParsInitNamedFamily(MyDataSection):
        key = "pars_init_registry_isolation_block"
        template_families = ("pars_init",)

    class ParsInitRegisteredWithSameFamilyAndKey(ParsInitSection):
        key = "pars_init_registry_isolation_block"
        template_families = ("pars_init",)

    assert MyDataRegisteredInParsInitNamedFamily in MyDataSection.registered_section_classes(
        template_families="pars_init"
    )
    assert ParsInitRegisteredWithSameFamilyAndKey not in MyDataSection.registered_section_classes(
        template_families="pars_init"
    )
    assert ParsInitRegisteredWithSameFamilyAndKey in ParsInitSection.registered_section_classes(
        template_families="pars_init"
    )
    assert MyDataRegisteredInParsInitNamedFamily not in ParsInitSection.registered_section_classes(
        template_families="pars_init"
    )
    assert "pars_init_registry_isolation_block" in ParsInitTemplate.allowed_section_keys()


def test_pars_init_template_requires_explicit_registry_for_parameter_rendering():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"unknown_par": 1.23},
        tier_pars=[],
        get_file_sections=lambda file_key: (),
    )

    with pytest.raises(ValueError, match="Provide a ParameterRegistry"):
        ParsInitProgrammaticTemplate().render(context)


def test_pars_init_template_rejects_legacy_t_ref_in_full_pars_dict():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"T_ref": 300.15},
        tier_pars=[],
        get_file_sections=lambda file_key: (),
    )

    with pytest.raises(ValueError, match="ParsInitReferenceTemperatureSection"):
        RegistryParsInitProgrammaticTemplate().render(context)


def test_pars_init_template_rejects_legacy_t_ref_in_parameter_registry():
    parameter_registry = StdParameterRegistry()
    parameter_registry.add(require_parameter_definition("T_ref"))
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"kap_X": 0.25},
        tier_pars=[],
        get_file_sections=lambda file_key: (),
    )

    with pytest.raises(ValueError, match="ParsInitReferenceTemperatureSection"):
        RegistryParsInitProgrammaticTemplate(parameter_registry=parameter_registry, model="nat").render(context)


def test_pars_init_template_accepts_custom_parameter_registry():
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"unknown_par": 1.23},
        tier_pars=[],
        get_file_sections=lambda file_key: (),
    )
    parameter_registry = StdParameterRegistry()
    parameter_registry.add(ParameterDefinition(name="unknown_par", units="-", label="unknown parameter"))
    template = RegistryParsInitProgrammaticTemplate(parameter_registry=parameter_registry, model="nat")

    contents = template.render(context)

    assert "par.unknown_par = 1.23;" in contents
    assert "label.unknown_par = 'unknown parameter';" in contents


def test_registry_pars_init_substitution_template_accepts_custom_parameter_registry():
    parameter_registry = StdParameterRegistry()
    parameter_registry.add(ParameterDefinition(name="unknown_par", units="-", label="unknown parameter"))
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"unknown_par": 1.23},
        tier_pars=[],
    )

    contents = RegistryParsInitSubstitutionTemplate(
        source="$function_header\n$base_parameters\n$packing",
        parameter_registry=parameter_registry,
        model="nat",
    ).render(context)

    assert "par.unknown_par = 1.23;" in contents
    assert "label.unknown_par = 'unknown parameter';" in contents


def test_registry_multitier_pars_init_substitution_template_accepts_custom_parameter_registry():
    parameter_registry = StdParameterRegistry()
    parameter_registry.add(ParameterDefinition(name="unknown_par", units="-", label="unknown parameter"))
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"unknown_par": 1.23},
        tier_pars=["unknown_par"],
        entity_list=["entity_1"],
        tier_par_init_values={"unknown_par": {"entity_1": 1.0}},
    )

    contents = RegistryMultitierParsInitSubstitutionTemplate(
        source="$function_header\n$base_parameters\n$tier_parameter_loops\n$packing",
        parameter_registry=parameter_registry,
        model="nat",
    ).render(context)

    assert "par.unknown_par = 1.23;" in contents
    assert "varname = [par_name '_' entity_id];" in contents


def test_registry_multitier_pars_init_programmatic_template_accepts_custom_parameter_registry():
    parameter_registry = StdParameterRegistry()
    parameter_registry.add(ParameterDefinition(name="unknown_par", units="-", label="unknown parameter"))
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"unknown_par": 1.23},
        tier_pars=["unknown_par"],
        entity_list=["entity_1"],
        tier_par_init_values={"unknown_par": {"entity_1": 1.0}},
    )

    contents = RegistryMultitierParsInitProgrammaticTemplate(
        parameter_registry=parameter_registry,
        model="nat",
    ).render(context)

    assert "par.unknown_par = 1.23;" in contents
    assert "varname = [par_name '_' entity_id];" in contents


def test_run_template_renders_required_sections():
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={},
        get_file_sections=lambda file_key: (),
    )
    template = RunProgrammaticTemplate()

    contents = template.render(context)

    assert "pets = {'Test_species'};" in contents
    assert "estim_options('default');" in contents
    assert "[nsteps, converged, fval] = estim_pars;" in contents
    assert "estim_options('max_step_number'" not in contents


def test_run_template_required_sections_returns_complete_valid_tuple():
    template = RunProgrammaticTemplate(sections=RunProgrammaticTemplate.required_sections())

    assert tuple(section.key for section in template.get_sections()) == (
        "setup",
        "set_options",
        "estimation_call",
    )


def test_run_template_uses_only_user_provided_sections():
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={
            "n_steps": 10,
            "tol_simplex": 1e-4,
            "pars_init_method": 2,
            "n_runs": 3,
            "results_output_mode": 0,
        },
    )
    contents = RunProgrammaticTemplate(
        sections=_replace_run_section(
            RunProgrammaticTemplate.required_sections(),
            key="estimation_call",
            content="disp('custom estimation call');",
        )
    ).render(context)

    assert "disp('custom estimation call');" in contents
    assert "estim_options('default');" in contents


def test_run_source_template_uses_source_path_independently():
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={
            "n_steps": 10,
            "tol_simplex": 1e-4,
            "pars_init_method": 2,
            "n_runs": 3,
            "results_output_mode": 0,
        },
        get_file_sections=lambda _file_key: (),
    )
    source = "\n".join(
        [
            "$setup",
            "$set_options",
            "$estimation_call",
        ]
    )

    source_template_contents = RunSubstitutionTemplate(source=source).render(context)

    assert "pets = {'Test_species'};" in source_template_contents
    assert "estim_options('default');" in source_template_contents
    assert "[nsteps, converged, fval] = estim_pars;" in source_template_contents


def test_set_estim_options_section_rejects_missing_runtime_settings():
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={
            "n_steps": 10,
        },
        get_file_sections=lambda _file_key: (),
    )

    with pytest.raises(ValueError, match="Missing run setting 'tol_simplex'"):
        SetEstimOptionsSection(options=(SetTolSimplexOption(render_key="tol_simplex"),)).render(context)


def test_run_source_template_renders_only_referenced_sections():
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={
            "n_steps": 10,
            "tol_simplex": 1e-4,
            "pars_init_method": 2,
            "n_runs": 3,
            "results_output_mode": 0,
        },
        get_file_sections=lambda _file_key: (),
    )

    contents = RunSubstitutionTemplate(source="$setup").render(context)

    assert contents.startswith("clear;\nclose all;\n")
    assert "estim_options('max_step_number'" not in contents


def test_run_template_rejects_missing_required_sections():
    with pytest.raises(ValueError, match="Missing required run sections"):
        RunProgrammaticTemplate(sections=(InlineRunSection(key="setup", content="header"),))


def test_run_section_registration_updates_allowed_keys_automatically():
    class AutoRegisteredRunSection(RunSection):
        key = "auto_registered_run_block"
        template_families = ("run",)
        section_tags = ("algorithm",)

    assert "auto_registered_run_block" in RunProgrammaticTemplate.allowed_section_keys()


def test_section_registries_are_isolated_between_mydata_and_run_roots():
    class MyDataRegisteredInRunNamedFamily(MyDataSection):
        key = "shared_registry_isolation_block"
        template_families = ("run",)

    class RunRegisteredWithSameFamilyAndKey(RunSection):
        key = "shared_registry_isolation_block"
        template_families = ("run",)

    assert MyDataRegisteredInRunNamedFamily in MyDataSection.registered_section_classes(
        template_families="run"
    )
    assert RunRegisteredWithSameFamilyAndKey not in MyDataSection.registered_section_classes(
        template_families="run"
    )
    assert RunRegisteredWithSameFamilyAndKey in RunSection.registered_section_classes(
        template_families="run"
    )
    assert MyDataRegisteredInRunNamedFamily not in RunSection.registered_section_classes(
        template_families="run"
    )
    assert "shared_registry_isolation_block" in RunProgrammaticTemplate.allowed_section_keys()


def test_run_section_duplicate_registered_key_is_rejected():
    class FirstRegisteredRunSection(RunSection):
        key = "duplicate_run_block"
        template_families = ("run",)

    with pytest.raises(ValueError, match="Duplicate run section key 'duplicate_run_block'"):
        class DuplicateRegisteredRunSection(RunSection):
            key = "duplicate_run_block"
            template_families = ("run",)


def test_run_template_rejects_old_hook_constructor_arguments():
    with pytest.raises(TypeError):
        RunProgrammaticTemplate(pre_estimation_hook="disp('before');")


def test_add_path_section_renders_fixed_folders_in_order():
    context = SimpleNamespace(estimation_settings={})
    section = AddPathSection(["data_pipeline", "ode"])

    contents = section.render(context)

    assert contents.splitlines() == [
        "addpath('data_pipeline');",
        "addpath('ode');",
    ]


def test_add_path_section_accepts_path_objects_and_escapes_quotes():
    context = SimpleNamespace(estimation_settings={})
    folder = Path("data") / "Lucas's dataset"
    section = AddPathSection([folder])
    escaped_folder = str(folder).replace("'", "''")

    assert section.render(context) == f"addpath('{escaped_folder}');"


def test_add_path_section_rejects_non_collection_folders():
    with pytest.raises(TypeError, match="folders must be a list or tuple"):
        AddPathSection("data")


def test_add_path_section_rejects_non_pathlike_folder_items():
    with pytest.raises(TypeError, match="item 1 is int"):
        AddPathSection(["data", 1])


def test_add_path_section_registered_as_allowed_run_key():
    assert "add_paths" in RunProgrammaticTemplate.allowed_section_keys()


def test_estim_option_run_section_renders_initialization_and_ordered_options():
    context = SimpleNamespace(estimation_settings={"n_steps": 25, "method_key": "nm"})
    section = SetEstimOptionsSection(
        options=(
            SetMaxStepNumberOption(render_key="n_steps"),
            SetMethodOption(render_key="method_key"),
        )
    )

    contents = section.render(context)

    assert contents.splitlines() == [
        SetDefaultEstimOptions().render(context),
        "estim_options('max_step_number', 25);",
        "estim_options('method', 'nm');",
    ]


def test_algorithm_run_template_renders_fixed_and_runtime_settings():
    class DummyAlgorithm(AlgorithmRunTemplate):
        method = "nm"
        option_classes = {
            "n_steps": SetMaxStepNumberOption,
            "tol_simplex": SetTolSimplexOption,
        }

        def __init__(self, *, n_steps=None, tol_simplex=None):
            self._settings = {
                "n_steps": n_steps,
                "tol_simplex": tol_simplex,
            }
            super().__init__()

        def get_algorithm_settings(self):
            return dict(self._settings)

    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={"tol_simplex": 1e-4},
    )

    template = DummyAlgorithm(n_steps=25)
    contents = template.render(context)

    assert "estim_options('method', 'nm');" in contents
    assert "estim_options('max_step_number', 25);" in contents
    assert "estim_options('tol_simplex', 0.0001);" in contents
    assert "addpath(" not in contents
    assert template.get_fixed_settings() == {"n_steps": 25}
    assert template.get_render_time_settings() == {"tol_simplex": None}


def test_algorithm_run_template_appends_extra_options_and_post_estimation_sections():
    class DummyAlgorithm(AlgorithmRunTemplate):
        method = "nm"
        option_classes = {"n_steps": SetMaxStepNumberOption}

        def __init__(self):
            self._settings = {"n_steps": 25}
            super().__init__(
                extra_options=(SetFilterOption(1),),
                post_estimation_sections=(
                    InlineRunSection(key="save_predictions", content="disp('post estimation');"),
                ),
            )

        def get_algorithm_settings(self):
            return dict(self._settings)

    context = SimpleNamespace(species_name="Test_species", estimation_settings={})
    contents = DummyAlgorithm().render(context)

    assert contents.index("estim_options('max_step_number', 25);") < contents.index(
        "estim_options('filter', 1);"
    )
    assert contents.index("[nsteps, converged, fval] = estim_pars;") < contents.index(
        "disp('post estimation');"
    )


def test_algorithm_run_template_inserts_add_paths_after_setup_and_before_options():
    class DummyAlgorithm(AlgorithmRunTemplate):
        method = "nm"
        option_classes = {"n_steps": SetMaxStepNumberOption}

        def __init__(self):
            self._settings = {"n_steps": 25}
            super().__init__(add_path_dirs=("data_pipeline", "ode"))

        def get_algorithm_settings(self):
            return dict(self._settings)

    context = SimpleNamespace(species_name="Test_species", estimation_settings={})
    template = DummyAlgorithm()
    contents = template.render(context)

    assert template.add_path_dirs == ("data_pipeline", "ode")
    assert contents.index("check_my_pet(pets);") < contents.index("addpath('data_pipeline');")
    assert contents.index("addpath('data_pipeline');") < contents.index("addpath('ode');")
    assert contents.index("addpath('ode');") < contents.index("estim_options('default');")


def test_algorithm_run_template_rejects_invalid_add_path_dirs():
    class DummyAlgorithm(AlgorithmRunTemplate):
        method = "nm"

        def get_algorithm_settings(self):
            return {}

    with pytest.raises(TypeError, match="item 1 is int"):
        DummyAlgorithm(add_path_dirs=("data", 1))


def test_algorithm_run_template_rejects_unknown_option_keys_when_built_directly():
    class DummyAlgorithm(AlgorithmRunTemplate):
        method = "nm"
        option_classes = {"n_steps": SetMaxStepNumberOption}

        def get_algorithm_settings(self):
            return {"n_steps": 25}

    with pytest.raises(ValueError, match="Unsupported algorithm setting 'unknown'"):
        DummyAlgorithm().build_algorithm_option("unknown", 25)


def test_algorithm_run_template_reports_mixed_option_and_non_option_settings():
    class DummyAlgorithm(AlgorithmRunTemplate):
        method = "nm"
        option_classes = {"n_steps": SetMaxStepNumberOption}

        def __init__(self, *, n_steps=None, n_runs=None):
            self._settings = {
                "n_steps": n_steps,
                "n_runs": n_runs,
            }
            super().__init__()

        def get_algorithm_settings(self):
            return dict(self._settings)

    context = SimpleNamespace(species_name="Test_species", estimation_settings={"n_steps": 25})

    template = DummyAlgorithm(n_runs=3)
    contents = template.render(context)

    assert "estim_options('max_step_number', 25);" in contents
    assert "estim_options('n_runs'" not in contents
    assert template.get_fixed_settings() == {"n_runs": 3}
    assert template.get_render_time_settings() == {"n_steps": None}


def test_algorithm_run_template_reports_missing_render_time_settings():
    class DummyAlgorithm(AlgorithmRunTemplate):
        method = "nm"
        option_classes = {"tol_simplex": SetTolSimplexOption}

        def get_algorithm_settings(self):
            return {"tol_simplex": None}

    context = SimpleNamespace(species_name="Test_species", estimation_settings={})

    with pytest.raises(ValueError, match="Missing run setting 'tol_simplex'"):
        DummyAlgorithm().render(context)


def test_nelder_mead_uses_algorithm_run_template_settings():
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={"tol_simplex": 1e-4, "results_output_mode": 0},
    )

    template = NelderMead(
        n_steps=25,
        n_evals=100,
        simplex_size=0.25,
        pars_init_method=2,
        save_predictions=False,
    )
    contents = template.render(context)

    assert isinstance(template, AlgorithmRunTemplate)
    assert template.get_fixed_settings() == {
        "n_steps": 25,
        "n_evals": 100,
        "simplex_size": 0.25,
        "pars_init_method": 2,
    }
    assert template.get_render_time_settings() == {
        "tol_simplex": None,
        "results_output_mode": None,
    }
    assert "estim_options('method', 'nm');" in contents
    assert "estim_options('max_fun_evals', 100);" in contents
    assert "estim_options('simplex_size', 0.25);" in contents
    assert "estim_options('tol_simplex', 0.0001);" in contents
    assert "prdData" not in contents


def test_nelder_mead_accepts_add_path_dirs():
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={
            "n_steps": 25,
            "n_evals": 100,
            "simplex_size": 0.25,
            "tol_simplex": 1e-4,
            "pars_init_method": 2,
            "results_output_mode": 0,
        },
    )

    template = NelderMead(add_path_dirs=(Path("data_pipeline"), "ode"), save_predictions=False)
    contents = template.render(context)

    assert template.add_path_dirs == (str(Path("data_pipeline")), "ode")
    assert contents.index("check_my_pet(pets);") < contents.index(f"addpath('{Path('data_pipeline')}');")
    assert contents.index(f"addpath('{Path('data_pipeline')}');") < contents.index("addpath('ode');")
    assert contents.index("addpath('ode');") < contents.index("estim_options('default');")


def test_restarting_nelder_mead_renders_restart_loop():
    context = SimpleNamespace(species_name="Test_species", estimation_settings={})

    template = RestartingNelderMead(
        n_steps=25,
        n_evals=100,
        simplex_size=0.25,
        tol_simplex=1e-4,
        pars_init_method=2,
        n_runs=3,
        tol_restart=1e-5,
        results_output_mode=2,
        save_predictions=False,
    )
    contents = template.render(context)

    first_call = "[nsteps, converged, fval] = estim_pars;"
    assert contents.index(first_call) < contents.index("n_runs = 3;")
    assert "tol_restart = 1e-05;" in contents
    assert "while (abs(prev_fval - fval) > tol_restart) && (i <= n_runs) && ~converged" in contents
    assert "while (abs(prev_fval - fval) > tol_simplex)" not in contents
    assert "fprintf('Run %d/%d\\n', i, n_runs)" in contents
    assert contents.count("estim_options('results_output', 0);") == 2
    assert "estim_options('pars_init_method', 1);" in contents
    assert "estim_options('method', 'no');" in contents
    assert "estim_options('results_output', 2);" in contents
    assert contents.index("estim_options('method', 'no');") < contents.index(
        "estim_options('results_output', 2);"
    )
    assert contents.index("estim_options('method', 'no');") < contents.rindex("estim_pars;")
    assert "prdData" not in contents


def test_restarting_nelder_mead_accepts_add_path_dirs_before_restart_behavior():
    context = SimpleNamespace(species_name="Test_species", estimation_settings={})

    template = RestartingNelderMead(
        n_steps=25,
        n_evals=100,
        simplex_size=0.25,
        tol_simplex=1e-4,
        pars_init_method=2,
        n_runs=3,
        tol_restart=1e-5,
        results_output_mode=2,
        add_path_dirs=("data_pipeline",),
        save_predictions=False,
    )
    contents = template.render(context)

    assert contents.index("addpath('data_pipeline');") < contents.index("estim_options('default');")
    assert contents.index("addpath('data_pipeline');") < contents.index("[nsteps, converged, fval] = estim_pars;")
    assert contents.index("[nsteps, converged, fval] = estim_pars;") < contents.index("n_runs = 3;")


def test_restarting_nelder_mead_validates_restart_settings():
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={
            "n_steps": 25,
            "n_evals": 100,
            "simplex_size": 0.25,
            "tol_simplex": 1e-4,
            "pars_init_method": 2,
            "results_output_mode": 0,
        },
    )

    with pytest.raises(TypeError, match="expects an integer value"):
        RestartingNelderMead(n_runs=1.5, tol_restart=1e-5).render(context)
    with pytest.raises(ValueError, match="positive numeric value"):
        RestartingNelderMead(n_runs=3, tol_restart=0).render(context)


def test_restart_loop_section_binds_alternation_at_construction():
    default_section = RestartLoopSection()
    alternating_section = RestartLoopSection(alternate_simplex_size=True)

    assert "${alternate_simplex_size}" not in default_section.get_matlab_code()
    assert "simplex_size = -simplex_size;" not in default_section.get_matlab_code()
    assert "${alternate_simplex_size}" not in alternating_section.get_matlab_code()
    assert "simplex_size = -simplex_size;" in alternating_section.get_matlab_code()
    with pytest.raises(TypeError, match="alternate_simplex_size must be a bool"):
        RestartLoopSection(alternate_simplex_size=1)


def test_alternating_restart_nelder_mead_renders_global_simplex_and_alternation():
    context = SimpleNamespace(species_name="Test_species", estimation_settings={})

    template = AlternatingRestartNelderMead(
        n_steps=25,
        n_evals=100,
        simplex_size=0.25,
        tol_simplex=1e-4,
        pars_init_method=2,
        n_runs=3,
        tol_restart=1e-5,
        results_output_mode=2,
        save_predictions=False,
    )
    contents = template.render(context)

    assert "global simplex_size" in contents
    assert "simplex_size = 0.25;" in contents
    assert "estim_options('simplex_size', simplex_size);" in contents
    assert "simplex_size = -simplex_size;" in contents
    assert contents.index("simplex_size = -simplex_size;") < contents.index(
        "    [nsteps, converged, fval] = estim_pars;"
    )
    assert "n_runs = 3;" in contents
    assert "tol_restart = 1e-05;" in contents
    assert "estim_options('method', 'no');" in contents
    assert "estim_options('results_output', 2);" in contents
    assert "prdData" not in contents


def test_set_estim_options_section_defaults_to_initialization_only_when_options_are_empty():
    context = SimpleNamespace(estimation_settings={})

    assert SetEstimOptionsSection().render(context) == "estim_options('default');"
    assert SetEstimOptionsSection(options=()).render(context) == "estim_options('default');"


def test_estim_option_run_section_rejects_tuple_options():
    with pytest.raises(TypeError, match="EstimOption instances"):
        SetEstimOptionsSection(options=(("max_step_number", 25),))


def test_numeric_estim_option_accepts_numeric_values_and_rejects_strings_and_bools():
    context = SimpleNamespace(estimation_settings={})

    assert SetTolSimplexOption(0.25).render(context) == "estim_options('tol_simplex', 0.25);"
    with pytest.raises(TypeError, match="expects a numeric value"):
        SetTolSimplexOption("0.25").render(context)
    with pytest.raises(TypeError, match="expects a numeric value"):
        SetTolSimplexOption(True).render(context)


def test_integer_estim_option_accepts_integers_and_rejects_non_integers():
    context = SimpleNamespace(estimation_settings={})

    assert isinstance(SetMaxStepNumberOption(25), IntegerEstimOption)
    assert SetMaxStepNumberOption(25).render(context) == "estim_options('max_step_number', 25);"
    assert SetMaxFunEvalsOption(25).render(context) == "estim_options('max_fun_evals', 25);"
    assert SetMaxStepNumberOption(np.int64(25)).render(context) == "estim_options('max_step_number', 25);"
    with pytest.raises(TypeError, match="expects an integer value"):
        SetMaxStepNumberOption(1.5).render(context)
    with pytest.raises(TypeError, match="expects an integer value"):
        SetMaxFunEvalsOption(1.5).render(context)
    with pytest.raises(TypeError, match="expects an integer value"):
        SetMaxStepNumberOption(True).render(context)
    with pytest.raises(ValueError, match="positive numeric value"):
        SetMaxStepNumberOption(0).render(context)


def test_continuous_numeric_estim_options_still_accept_floats():
    context = SimpleNamespace(estimation_settings={})

    assert SetSimplexSizeOption(0.25).render(context) == "estim_options('simplex_size', 0.25);"
    assert SetTolSimplexOption(1e-4).render(context) == "estim_options('tol_simplex', 0.0001);"


def test_enum_estim_options_reject_float_equivalent_values():
    context = SimpleNamespace(estimation_settings={})

    with pytest.raises(TypeError, match="expects an integer value"):
        SetParsInitMethodOption(1.0).render(context)
    with pytest.raises(TypeError, match="expects an integer value"):
        SetResultsOutputOption(1.0).render(context)
    with pytest.raises(TypeError, match="expects an integer value"):
        SetFilterOption(1.0).render(context)


def test_string_estim_option_accepts_strings_and_rejects_numeric_values():
    context = SimpleNamespace(estimation_settings={})

    assert SetMethodOption("nm").render(context) == "estim_options('method', 'nm');"
    with pytest.raises(TypeError, match="expects a string value"):
        SetMethodOption(1).render(context)


def test_known_estim_option_allowed_values_are_enforced():
    context = SimpleNamespace(estimation_settings={})

    with pytest.raises(ValueError, match="expected one of"):
        SetMethodOption("bad_method").render(context)
    with pytest.raises(ValueError, match="expected one of"):
        SetParsInitMethodOption(4).render(context)
    with pytest.raises(ValueError, match="expected one of"):
        SetResultsOutputOption(7).render(context)
    with pytest.raises(ValueError, match="expected one of"):
        SetFilterOption(2).render(context)


def test_estim_option_resolves_render_time_values_and_rejects_missing_keys():
    context = SimpleNamespace(estimation_settings={"n_steps": 25})

    assert SetMaxStepNumberOption(render_key="n_steps").render(context) == "estim_options('max_step_number', 25);"
    assert SetMaxStepNumberOption(RunSetting("n_steps")).render(context) == "estim_options('max_step_number', 25);"
    with pytest.raises(ValueError, match="Missing run setting 'tol_simplex'"):
        SetTolSimplexOption(render_key="tol_simplex").render(context)
    with pytest.raises(ValueError, match="Missing run setting 'tol_simplex'"):
        SetTolSimplexOption(RunSetting("tol_simplex")).render(context)


def test_estim_option_create_variable_renders_assignment_and_option_call():
    context = SimpleNamespace(estimation_settings={"tol_simplex": 1e-4})
    option = SetTolSimplexOption(render_key="tol_simplex", create_variable=True)

    assert option.render(context).splitlines() == [
        "tol_simplex = 0.0001;",
        "estim_options('tol_simplex', tol_simplex);",
    ]


def test_estim_option_create_global_variable_renders_global_assignment_and_option_call():
    context = SimpleNamespace(estimation_settings={"tol_simplex": 1e-4})
    option = SetTolSimplexOption(render_key="tol_simplex", create_global_variable=True)

    assert option.render(context).splitlines() == [
        "global tol_simplex",
        "tol_simplex = 0.0001;",
        "estim_options('tol_simplex', tol_simplex);",
    ]


def test_custom_estim_option_validation_is_user_owned():
    class CustomStringOption(StringEstimOption):
        argument_name = "custom_label"

    class CustomPositiveOption(NumericEstimOption):
        argument_name = "custom_positive"
        positive = True

    context = SimpleNamespace(estimation_settings={})

    assert CustomStringOption("O'Brien").render(context) == "estim_options('custom_label', 'O''Brien');"
    with pytest.raises(ValueError, match="positive numeric value"):
        CustomPositiveOption(0).render(context)


def test_estim_option_validates_variable_names_when_creating_variables():
    with pytest.raises(ValueError, match="not a valid MATLAB identifier"):
        EstimOption(argument_name="not-valid", value=1, create_variable=True)


def test_programmatic_template_rejects_unknown_section_keys_at_construction():
    class DummySection:
        def __init__(self, key: str, content: str):
            self.key = key
            self.content = content

        def validate(self, allowed_keys):
            if self.key not in allowed_keys:
                raise ValueError(
                    f"Unsupported dummy template key '{self.key}'. "
                    f"Expected one of: {', '.join(allowed_keys)}."
                )

        def render(self, _context) -> str:
            return self.content

    class DummyProgrammaticTemplate(ProgrammaticTemplate):
        def __init__(self, *, sections):
            super().__init__(
                sections=sections,
                allowed_section_keys=("header", "body"),
                required_section_keys=("header", "body"),
                template_label="dummy",
            )

        def get_section_key(self, section) -> str:
            return section.key

        def render_section(self, section, context) -> str:
            return section.render(context)

    with pytest.raises(ValueError, match="Unsupported dummy template key 'footer'"):
        DummyProgrammaticTemplate(
            sections=(
                DummySection("header", "header"),
                DummySection("body", "body"),
                DummySection("footer", "footer"),
            ),
        )


def test_programmatic_template_rejects_missing_required_sections_at_construction():
    class DummySection:
        def __init__(self, key: str, content: str):
            self.key = key
            self.content = content

        def validate(self, allowed_keys):
            if self.key not in allowed_keys:
                raise ValueError

        def render(self, _context) -> str:
            return self.content

    class DummyProgrammaticTemplate(ProgrammaticTemplate):
        def __init__(self, *, sections):
            super().__init__(
                sections=sections,
                allowed_section_keys=("header", "body"),
                required_section_keys=("header", "body"),
                template_label="dummy",
            )

        def get_section_key(self, section) -> str:
            return section.key

        def render_section(self, section, context) -> str:
            return section.render(context)

    with pytest.raises(ValueError, match="Missing required dummy sections"):
        DummyProgrammaticTemplate(sections=(DummySection("header", "header"),))


def test_programmatic_template_rejects_duplicate_sections_at_construction():
    class DummySection:
        def __init__(self, key: str, content: str):
            self.key = key
            self.content = content

        def validate(self, allowed_keys):
            if self.key not in allowed_keys:
                raise ValueError

        def render(self, _context) -> str:
            return self.content

    class DummyProgrammaticTemplate(ProgrammaticTemplate):
        def __init__(self, *, sections):
            super().__init__(
                sections=sections,
                allowed_section_keys=("header", "body"),
                required_section_keys=("header", "body"),
                template_label="dummy",
            )

        def get_section_key(self, section) -> str:
            return section.key

        def render_section(self, section, context) -> str:
            return section.render(context)

    with pytest.raises(ValueError, match="Duplicate dummy section key 'header'"):
        DummyProgrammaticTemplate(
            sections=(
                DummySection("header", "header one"),
                DummySection("header", "header two"),
                DummySection("body", "body"),
            ),
        )


def test_programmatic_template_render_preserves_section_order():
    class DummySection:
        def __init__(self, key: str, content: str):
            self.key = key
            self.content = content

        def validate(self, allowed_keys):
            if self.key not in allowed_keys:
                raise ValueError

        def render(self, _context) -> str:
            return self.content

    class DummyProgrammaticTemplate(ProgrammaticTemplate):
        def __init__(self, *, sections):
            super().__init__(
                sections=sections,
                allowed_section_keys=("header", "body"),
                required_section_keys=("header", "body"),
                template_label="dummy",
            )

        def get_section_key(self, section) -> str:
            return section.key

        def render_section(self, section, context) -> str:
            return section.render(context)

    contents = DummyProgrammaticTemplate(
        sections=(
            DummySection("body", "body"),
            DummySection("header", "header"),
        )
    ).render(SimpleNamespace())

    assert contents == "body\n\nheader"


def test_mydata_source_template_does_not_depend_on_programmatic_template(monkeypatch, tmp_path):
    context = _build_multitier_context(tmp_path)

    def fail(*args, **kwargs):
        raise AssertionError("Source template path should not instantiate or depend on MyDataProgrammaticTemplate")

    monkeypatch.setattr(MyDataProgrammaticTemplate, "render", fail)
    monkeypatch.setattr(MultitierMyDataProgrammaticTemplate, "render", fail)

    assert MultitierMyDataSubstitutionTemplate(source="$function_header").render(context).startswith(
        "function [data, auxData, metaData, txtData, weights] = mydata_Test_species"
    )


def test_pars_init_source_template_does_not_depend_on_programmatic_template(monkeypatch):
    context = SimpleNamespace(
        species_name="Test_species",
        full_pars_dict={"p_Am": 12.5},
        tier_pars=["p_Am"],
        tier_name="top",
        entity_list=["entity_1"],
        tier_par_init_values={"p_Am": {"entity_1": 1.0}},
    )

    def fail(*args, **kwargs):
        raise AssertionError("Source template path should not instantiate or depend on ParsInitProgrammaticTemplate")

    monkeypatch.setattr(ParsInitProgrammaticTemplate, "render", fail)
    monkeypatch.setattr(MultitierParsInitProgrammaticTemplate, "render", fail)

    assert MultitierParsInitSubstitutionTemplate(source="$function_header").render(context).startswith(
        "function [par, metaPar, txtPar] = pars_init_Test_species(metaData)"
    )


def test_run_source_template_does_not_depend_on_programmatic_template(monkeypatch):
    context = SimpleNamespace(
        species_name="Test_species",
        estimation_settings={
            "n_steps": 10,
            "tol_simplex": 1e-4,
            "pars_init_method": 2,
            "n_runs": 3,
            "results_output_mode": 0,
        },
    )

    def fail(*args, **kwargs):
        raise AssertionError("Source template path should not instantiate or depend on RunProgrammaticTemplate")

    monkeypatch.setattr(RunProgrammaticTemplate, "render", fail)

    assert RunSubstitutionTemplate(source="$setup").render(context).startswith(
        "clear;\nclose all;\n"
    )
