import json
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from DEBtoolPyIF.multitier import TierEstimator

from tests.unit.multitier_test_helpers import (
    build_grouped_tier_estimator,
    build_mixed_tier_estimator,
    build_tier_estimator,
)


def test_save_results_writes_backward_compatible_csvs_and_metadata(template_folder):
    tier = build_tier_estimator(template_folder)

    estimation_settings = {"n_runs": 5, "n_steps": 10}
    tier.estimate(
        save_results=True,
        print_results=False,
        hide_output=True,
        estimation_settings=estimation_settings,
    )

    expected_files = {"pars.csv", "entity_data_errors.csv", "group_data_errors.csv", "result_metadata.json"}
    assert set(TierEstimator.OUTPUT_FILES) == expected_files
    for filename in expected_files:
        assert (tier.output_folder / filename).is_file()

    metadata = json.loads((tier.output_folder / "result_metadata.json").read_text(encoding="utf-8"))
    assert metadata["schema_version"] == TierEstimator.RESULT_SCHEMA_VERSION
    assert metadata["stable_output_files"] == TierEstimator.OUTPUT_FILES
    assert metadata["tier_name"] == "tier_1"
    assert metadata["species_name"] == "Test_species"
    assert metadata["output_folder"] == str((template_folder / "output").resolve())
    assert metadata["tier_entities"] == ["entity_1"]
    assert metadata["tier_groups"] == ["group_1"]
    assert metadata["tier_parameters"] == ["par_a"]
    assert metadata["estimation_settings"] == estimation_settings
    assert metadata["estimation_start_time"] is not None
    assert metadata["estimation_end_time"] is not None
    assert metadata["elapsed_duration_seconds"] >= 0
    assert len(metadata["estimation_iterations"]) == 1
    assert metadata["estimation_iterations"][0]["estimation_target_type"] == "entity"
    assert metadata["estimation_iterations"][0]["estimation_target_name"] == "entity_1"
    assert metadata["estimation_iterations"][0]["entity_list"] == ["entity_1"]
    assert metadata["estimation_iterations"][0]["estimation_start_time"] is not None
    assert metadata["estimation_iterations"][0]["estimation_end_time"] is not None
    assert metadata["estimation_iterations"][0]["elapsed_duration_seconds"] >= 0
    assert metadata["estimation_iterations"][0]["success"] is True


def test_load_results_restores_saved_metadata_and_tables(template_folder):
    tier = build_tier_estimator(template_folder)

    estimation_settings = {"n_runs": 7, "n_steps": 15}
    tier.estimate(
        save_results=True,
        print_results=False,
        hide_output=True,
        estimation_settings=estimation_settings,
    )

    loaded_tier = build_tier_estimator(template_folder)
    loaded_tier.load_results()

    assert_frame_equal(loaded_tier.pars_df, tier.pars_df, check_dtype=False)
    assert_frame_equal(loaded_tier.entity_data_errors, tier.entity_data_errors, check_dtype=False)
    assert_frame_equal(loaded_tier.group_data_errors, tier.group_data_errors, check_dtype=False)
    assert loaded_tier.tier_pars == ["par_a"]
    assert loaded_tier.tier_entities == ["entity_1"]
    assert loaded_tier.tier_groups == ["group_1"]
    assert loaded_tier.estimation_settings == estimation_settings
    assert loaded_tier.estim_start_time == pd.Timestamp(tier.result_metadata["estimation_start_time"])
    assert loaded_tier.estim_end_time == pd.Timestamp(tier.result_metadata["estimation_end_time"])
    assert loaded_tier.result_metadata == tier.result_metadata
    assert len(loaded_tier.estimation_iterations) == 1
    assert loaded_tier.estimation_iterations[0]["estimation_target_name"] == "entity_1"
    assert loaded_tier.estimation_iterations[0]["success"] is True


def test_load_results_remains_compatible_without_metadata_file(template_folder):
    tier = build_tier_estimator(template_folder)
    tier.estimate(
        save_results=True,
        print_results=False,
        hide_output=True,
        estimation_settings={"n_runs": 2, "n_steps": 8},
    )

    (tier.output_folder / "result_metadata.json").unlink()

    loaded_tier = build_tier_estimator(template_folder)
    loaded_tier.estimation_settings = {"stale": True}
    loaded_tier.estim_start_time = pd.Timestamp("2024-01-01T00:00:00")
    loaded_tier.estim_end_time = pd.Timestamp("2024-01-01T00:01:00")
    loaded_tier.load_results()

    assert loaded_tier.result_metadata is None
    assert loaded_tier.estimation_settings is None
    assert loaded_tier.estim_start_time is None
    assert loaded_tier.estim_end_time is None
    assert loaded_tier.estimation_iterations == []
    assert list(loaded_tier.pars_df.columns) == ["par_a"]


def test_group_result_metadata_preserves_iteration_output_folders(template_folder):
    tier = build_grouped_tier_estimator(template_folder)

    tier.estimate(
        save_results=True,
        print_results=False,
        hide_output=True,
        estimation_settings={"n_runs": 4, "n_steps": 12},
    )

    metadata = json.loads((tier.output_folder / "result_metadata.json").read_text(encoding="utf-8"))
    assert len(metadata["estimation_iterations"]) == 2
    assert [iteration["estimation_target_name"] for iteration in metadata["estimation_iterations"]] == [
        "group_1",
        "group_2",
    ]
    assert [Path(iteration["output_folder"]).name for iteration in metadata["estimation_iterations"]] == [
        "group_1",
        "group_2",
    ]


def test_save_and_load_results_preserve_mixed_group_and_entity_iteration_metadata(template_folder):
    tier = build_mixed_tier_estimator(template_folder)

    estimation_settings = {"n_runs": 4, "n_steps": 12}
    tier.estimate(
        save_results=True,
        print_results=False,
        hide_output=True,
        estimation_settings=estimation_settings,
    )

    metadata = json.loads((tier.output_folder / "result_metadata.json").read_text(encoding="utf-8"))
    assert metadata["estimation_settings"] == estimation_settings
    assert [iteration["estimation_target_name"] for iteration in metadata["estimation_iterations"]] == [
        "Pen_2",
        "Pen_3",
        "Pen_4",
        "Pen_5",
        "PT42",
    ]
    assert [iteration["estimation_target_type"] for iteration in metadata["estimation_iterations"]] == [
        "group",
        "group",
        "group",
        "group",
        "entity",
    ]
    assert [Path(iteration["output_folder"]).name for iteration in metadata["estimation_iterations"]] == [
        "Pen_2",
        "Pen_3",
        "Pen_4",
        "Pen_5",
        "PT42",
    ]

    loaded_tier = build_mixed_tier_estimator(template_folder)
    loaded_tier.load_results()

    assert_frame_equal(loaded_tier.pars_df, tier.pars_df, check_dtype=False)
    assert loaded_tier.result_metadata == tier.result_metadata
    assert [iteration["estimation_target_name"] for iteration in loaded_tier.estimation_iterations] == [
        "Pen_2",
        "Pen_3",
        "Pen_4",
        "Pen_5",
        "PT42",
    ]
    assert [iteration["estimation_target_type"] for iteration in loaded_tier.estimation_iterations] == [
        "group",
        "group",
        "group",
        "group",
        "entity",
    ]
