from pathlib import Path

import pytest

from DEBtoolPyIF.multitier import TierEstimator, TierHierarchy


class FakeTierData:
    def __init__(self):
        self.groups = ["group_1"]
        self.entities = ["entity_1"]
        self.entity_data_types = ["obs"]
        self.group_data_types = ["group_obs"]


class FakeGroupedTierData:
    def __init__(self):
        self.groups = ["group_1", "group_2"]
        self.entities = ["entity_1", "entity_2"]
        self.entity_data_types = ["obs"]
        self.group_data_types = ["group_obs"]
        self.group_to_entities = {
            "group_1": ["entity_1"],
            "group_2": ["entity_2"],
        }

    def get_entity_list_of_group(self, group_id):
        return list(self.group_to_entities[group_id])


class FakeMixedTierData:
    def __init__(self):
        self.groups = ["Pen_2", "Pen_3", "Pen_4", "Pen_5"]
        self.entities = [
            "PT20",
            "PT21",
            "PT30",
            "PT31",
            "PT40",
            "PT41",
            "PT50",
            "PT51",
            "PT42",
        ]
        self.entity_data_types = ["obs"]
        self.group_data_types = ["group_obs"]
        self.group_to_entities = {
            "Pen_2": ["PT20", "PT21"],
            "Pen_3": ["PT30", "PT31"],
            "Pen_4": ["PT40", "PT41"],
            "Pen_5": ["PT50", "PT51"],
        }

    def get_entity_list_of_group(self, group_id):
        return list(self.group_to_entities[group_id])


class FakeRunner:
    def __init__(self):
        self.estim_files_dir = None

    def run_estimation(self, hide_output=True):
        return True

    def fetch_pars_from_mat_file(self):
        return {"par_a": 1.23}

    def fetch_errors_from_mat_file(self):
        return {}


class FakeGroupedRunner(FakeRunner):
    def fetch_pars_from_mat_file(self):
        group_name = Path(self.estim_files_dir).name
        if group_name == "group_1":
            return {"par_a_entity_1": 1.11}
        if group_name == "group_2":
            return {"par_a_entity_2": 2.22}
        raise AssertionError(f"Unexpected estimation folder: {self.estim_files_dir}")


class FakeMixedRunner(FakeRunner):
    FOLDER_TO_PARS = {
        "Pen_2": {"par_a_PT20": 2.0, "par_a_PT21": 2.1},
        "Pen_3": {"par_a_PT30": 3.0, "par_a_PT31": 3.1},
        "Pen_4": {"par_a_PT40": 4.0, "par_a_PT41": 4.1},
        "Pen_5": {"par_a_PT50": 5.0, "par_a_PT51": 5.1},
        "PT42": {"par_a_PT42": 42.0},
    }

    def fetch_pars_from_mat_file(self):
        folder_name = Path(self.estim_files_dir).name
        if folder_name not in self.FOLDER_TO_PARS:
            raise AssertionError(f"Unexpected estimation folder: {self.estim_files_dir}")
        return self.FOLDER_TO_PARS[folder_name]


class FakeTierStructure:
    def __init__(self):
        self.species_name = "Test_species"
        self.data = {"tier_1": FakeTierData()}
        self.estimation_runner = FakeRunner()
        self.tiers = {}
        self.entity_hierarchy = TierHierarchy(
            tier_names=["tier_1"],
            entities={"tier_1": ["entity_1"]},
        )


class FakeGroupedTierStructure:
    def __init__(self):
        self.species_name = "Test_species"
        self.data = {"tier_1": FakeGroupedTierData()}
        self.estimation_runner = FakeGroupedRunner()
        self.tiers = {}
        self.entity_hierarchy = TierHierarchy(
            tier_names=["tier_1"],
            entities={"tier_1": ["entity_1", "entity_2"]},
        )


class FakeMixedTierStructure:
    def __init__(self):
        self.species_name = "Test_species"
        self.data = {"tier_1": FakeMixedTierData()}
        self.estimation_runner = FakeMixedRunner()
        self.tiers = {}
        self.entity_hierarchy = TierHierarchy(
            tier_names=["tier_1"],
            entities={
                "tier_1": ["PT20", "PT21", "PT30", "PT31", "PT40", "PT41", "PT50", "PT51", "PT42"]
            },
        )


@pytest.fixture
def template_folder(tmp_path):
    folder = tmp_path / "templates"
    folder.mkdir()
    species_name = "Test_species"
    for prefix in ("mydata", "pars_init", "predict", "run"):
        (folder / f"{prefix}_{species_name}.m").write_text("% template\n", encoding="utf-8")
    return folder


def build_tier_estimator(template_folder: Path):
    tier_structure = FakeTierStructure()
    tier = TierEstimator(
        tier_structure=tier_structure,
        tier_name="tier_1",
        tier_pars=["par_a"],
        template_folder=str(template_folder),
        output_folder=str(template_folder / "output"),
    )
    tier_structure.tiers["tier_1"] = tier
    tier.code_generator.generate_code = lambda entity_list, pseudo_data_weight=0.1: None
    return tier


def build_grouped_tier_estimator(template_folder: Path):
    tier_structure = FakeGroupedTierStructure()
    tier = TierEstimator(
        tier_structure=tier_structure,
        tier_name="tier_1",
        tier_pars=["par_a"],
        template_folder=str(template_folder),
        output_folder=str(template_folder / "grouped_output"),
    )
    tier_structure.tiers["tier_1"] = tier
    tier.code_generator.generate_code = lambda entity_list, pseudo_data_weight=0.1: None
    return tier


def build_mixed_tier_estimator(template_folder: Path):
    tier_structure = FakeMixedTierStructure()
    tier = TierEstimator(
        tier_structure=tier_structure,
        tier_name="tier_1",
        tier_pars=["par_a"],
        template_folder=str(template_folder),
        output_folder=str(template_folder / "mixed_output"),
    )
    tier_structure.tiers["tier_1"] = tier
    tier.code_generator.generate_code = lambda entity_list, pseudo_data_weight=0.1: None
    return tier
