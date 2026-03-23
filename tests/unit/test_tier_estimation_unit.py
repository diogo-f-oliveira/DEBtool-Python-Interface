import pandas as pd
import pytest

from tests.unit.multitier_test_helpers import (
    build_grouped_tier_estimator,
    build_mixed_tier_estimator,
    build_tier_estimator,
)


def test_estimate_accepts_settings_and_persists_them(template_folder):
    tier = build_tier_estimator(template_folder)

    estimation_settings = {"n_runs": 5, "n_steps": 10}
    tier.estimate(
        save_results=False,
        print_results=False,
        hide_output=True,
        estimation_settings=estimation_settings,
    )

    assert tier.estimation_settings == estimation_settings
    assert tier.pars_df.loc["entity_1", "par_a"] == 1.23


def test_tier_estimator_converts_string_paths_to_path_objects(template_folder):
    tier = build_tier_estimator(template_folder)

    assert tier.template_folder == template_folder
    assert tier.output_folder == template_folder / "output"


def test_estimate_requires_settings_when_no_default_exists(template_folder):
    tier = build_tier_estimator(template_folder)

    with pytest.raises(ValueError, match="Estimation settings must be provided"):
        tier.estimate(save_results=False, print_results=False, hide_output=True)


def test_estimate_reuses_last_settings_when_not_overridden(template_folder):
    tier = build_tier_estimator(template_folder)

    estimation_settings = {"n_runs": 3, "n_steps": 20}
    tier.estimate(
        save_results=False,
        print_results=False,
        hide_output=True,
        estimation_settings=estimation_settings,
    )

    tier.estimate(save_results=False, print_results=False, hide_output=True)

    assert tier.estimation_settings == estimation_settings


def test_estimate_tracks_per_group_iteration_times(template_folder):
    tier = build_grouped_tier_estimator(template_folder)

    tier.estimate(
        save_results=True,
        print_results=False,
        hide_output=True,
        estimation_settings={"n_runs": 4, "n_steps": 12},
    )

    assert len(tier.estimation_iterations) == 2
    assert [iteration["estimation_target_name"] for iteration in tier.estimation_iterations] == ["group_1", "group_2"]
    assert [iteration["estimation_target_type"] for iteration in tier.estimation_iterations] == ["group", "group"]
    assert [iteration["entity_list"] for iteration in tier.estimation_iterations] == [["entity_1"], ["entity_2"]]
    assert all(iteration["success"] is True for iteration in tier.estimation_iterations)
    assert all(iteration["elapsed_duration_seconds"] >= 0 for iteration in tier.estimation_iterations)


def test_estimate_mixes_group_and_standalone_entity_iterations(template_folder):
    tier = build_mixed_tier_estimator(template_folder)

    tier.estimate(
        save_results=False,
        print_results=False,
        hide_output=True,
        estimation_settings={"n_runs": 4, "n_steps": 12},
    )

    assert [iteration["estimation_target_name"] for iteration in tier.estimation_iterations] == [
        "Pen_2",
        "Pen_3",
        "Pen_4",
        "Pen_5",
        "PT42",
    ]
    assert [iteration["estimation_target_type"] for iteration in tier.estimation_iterations] == [
        "group",
        "group",
        "group",
        "group",
        "entity",
    ]
    assert [iteration["entity_list"] for iteration in tier.estimation_iterations] == [
        ["PT20", "PT21"],
        ["PT30", "PT31"],
        ["PT40", "PT41"],
        ["PT50", "PT51"],
        ["PT42"],
    ]
    assert [(tier.output_folder / folder_name).is_dir() for folder_name in ["Pen_2", "Pen_3", "Pen_4", "Pen_5", "PT42"]] == [
        True,
        True,
        True,
        True,
        True,
    ]
    assert tier.pars_df.loc["PT20", "par_a"] == 2.0
    assert tier.pars_df.loc["PT21", "par_a"] == 2.1
    assert tier.pars_df.loc["PT42", "par_a"] == 42.0
    assert tier.pars_df.notna().all().all()


def test_estimate_requested_entities_expands_group_and_warns(template_folder):
    tier = build_mixed_tier_estimator(template_folder)

    with pytest.warns(UserWarning, match="Pen_2"):
        tier.estimate(
            save_results=False,
            print_results=False,
            hide_output=True,
            estimation_settings={"n_runs": 4, "n_steps": 12},
            entity_list=["PT20", "PT42"],
        )

    assert [iteration["estimation_target_name"] for iteration in tier.estimation_iterations] == [
        "Pen_2",
        "PT42",
    ]
    assert [iteration["estimation_target_type"] for iteration in tier.estimation_iterations] == [
        "group",
        "entity",
    ]
    assert [iteration["entity_list"] for iteration in tier.estimation_iterations] == [
        ["PT20", "PT21"],
        ["PT42"],
    ]
    assert tier.pars_df.loc["PT20", "par_a"] == 2.0
    assert tier.pars_df.loc["PT21", "par_a"] == 2.1
    assert tier.pars_df.loc["PT42", "par_a"] == 42.0
    assert pd.isna(tier.pars_df.loc["PT30", "par_a"])


def test_estimate_requested_entities_rejects_unknown_entities(template_folder):
    tier = build_mixed_tier_estimator(template_folder)

    with pytest.raises(ValueError, match="unknown entities: PT999"):
        tier.estimate(
            save_results=False,
            print_results=False,
            hide_output=True,
            estimation_settings={"n_runs": 4, "n_steps": 12},
            entity_list=["PT999"],
        )
