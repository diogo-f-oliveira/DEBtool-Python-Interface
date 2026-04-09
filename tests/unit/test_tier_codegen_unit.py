from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from DEBtoolPyIF.estimation_files.writer import write_estimation_file
from DEBtoolPyIF.multitier import MultitierMyDataSubstitutionTemplate, TierHierarchy
from DEBtoolPyIF.multitier.estimation_files import MultitierGenerationContext


class FakeCodegenTierData:
    def __init__(self, entity_data_types, group_data_types):
        self._entity_data_types = entity_data_types
        self._group_data_types = group_data_types

    def get_group_list_from_entity_list(self, entity_list):
        return []

    def get_entity_mydata_code(self, entity_list):
        return list(self._entity_data_types), ["% entity data"]

    def get_group_mydata_code(self, entity_list):
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
        return pd.DataFrame({"par_a": [1.0]}, index=list(entity_list))


def _write_required_templates(template_folder: Path, species_name: str):
    (template_folder / f"mydata_{species_name}.m").write_text(
        "\n".join(
            [
                "$function_header",
                "$metadata_block",
                "$entity_data_block",
                "$entity_data_types",
                "$group_data_block",
                "$group_data_types",
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
        ),
        encoding="utf-8",
    )
    for prefix in ("pars_init", "predict", "run"):
        (template_folder / f"{prefix}_{species_name}.m").write_text("% template\n", encoding="utf-8")


def test_generate_mydata_file_sorts_and_deduplicates_metadata_types(tmp_path):
    template_folder = tmp_path / "templates"
    output_folder = tmp_path / "output"
    template_folder.mkdir()
    output_folder.mkdir()

    tier_structure = FakeCodegenTierStructure()
    _write_required_templates(template_folder, tier_structure.species_name)

    tier_estimator = SimpleNamespace(
        name="top",
        tier_structure=tier_structure,
        output_folder=output_folder,
        tier_pars=["par_a"],
        extra_info="",
        estimation_settings={},
    )
    context = MultitierGenerationContext.from_tier_estimator(
        tier_estimator=tier_estimator,
        entity_list=["root_entity"],
        output_folder=output_folder,
    )
    write_estimation_file(
        "mydata",
        MultitierMyDataSubstitutionTemplate(
            source=template_folder / f"mydata_{tier_structure.species_name}.m"
        ),
        context,
    )

    contents = (output_folder / "mydata_Test_species.m").read_text(encoding="utf-8")

    assert "metaData.entity_data_types = {'alpha', 'beta', 'zeta'}; " in contents
    assert "metaData.group_data_types = {'group_a', 'group_m', 'group_z'}; " in contents
    assert contents.count("'alpha'") == 1
    assert contents.count("'group_a'") == 1
