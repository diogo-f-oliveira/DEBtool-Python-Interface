import json
from pathlib import Path

import pandas as pd
import pytest


GENERATED_MATLAB_FILE_PREFIXES = ("mydata", "pars_init", "predict", "run")


def _assert_non_empty_csv(csv_path: Path) -> pd.DataFrame:
    assert csv_path.is_file(), f"Expected result file was not created: {csv_path}"
    df = pd.read_csv(csv_path)
    assert not df.empty, f"Result file is empty: {csv_path}"
    return df


def _find_generated_matlab_files_by_prefix(tier_output_folder: Path, species_name: str) -> dict[str, list[Path]]:
    return {
        prefix: list(tier_output_folder.rglob(f"{prefix}_{species_name}.m"))
        for prefix in GENERATED_MATLAB_FILE_PREFIXES
    }


@pytest.mark.integration
def test_example_estimation_module_exposes_run_multitier_estimation(example_name, import_example_estimation_module):
    estimation_module = import_example_estimation_module(example_name)

    assert hasattr(estimation_module, "run_multitier_estimation"), (
        f"Missing run_multitier_estimation(multitier) in examples/{example_name}/estimation.py"
    )
    assert callable(estimation_module.run_multitier_estimation)


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.matlab
def test_estimation_runs_end_to_end_for_example(estimated_multitier):
    multitier, output_folder = estimated_multitier

    assert output_folder.is_dir(), f"Output folder was not created: {output_folder}"
    assert (output_folder / "entity_vs_tier.csv").is_file(), (
        f"Root multitier file missing: {output_folder / 'entity_vs_tier.csv'}"
    )

    for tier_name in multitier.tier_names:
        tier = multitier.tiers[tier_name]
        tier_output_folder = Path(tier.output_folder)

        assert tier_output_folder.is_dir(), f"Tier output folder missing for {tier_name}: {tier_output_folder}"
        assert tier.estimation_complete, f"Tier estimation did not complete for {tier_name}"
        generated_files = _find_generated_matlab_files_by_prefix(tier_output_folder, multitier.species_name)
        for prefix, matching_files in generated_files.items():
            assert matching_files, (
                f"Missing generated {prefix} MATLAB file under tier output folder for "
                f"{tier_name}: {tier_output_folder}"
            )

        for filename in (
            "pars.csv",
            "entity_data_errors.csv",
            "group_data_errors.csv",
            "result_metadata.json",
            "result_summary.json",
        ):
            assert (tier_output_folder / filename).is_file(), (
                f"Expected tier output file missing for {tier_name}: {filename}"
            )


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.matlab
def test_estimation_outputs_expected_result_files(estimated_multitier):
    multitier, _ = estimated_multitier

    for tier_name in multitier.tier_names:
        tier = multitier.tiers[tier_name]
        tier_output_folder = Path(tier.output_folder)

        _assert_non_empty_csv(tier_output_folder / "pars.csv")
        pars_df = pd.read_csv(tier_output_folder / "pars.csv", index_col="entity")
        assert pars_df.index.name == "entity"
        assert list(pars_df.columns) == list(tier.pars_df.columns)
        assert set(pars_df.index) == set(tier.pars_df.index)

        _assert_non_empty_csv(tier_output_folder / "entity_data_errors.csv")
        entity_errors_df = pd.read_csv(tier_output_folder / "entity_data_errors.csv", index_col=["tier", "entity"])
        assert list(entity_errors_df.index.names) == ["tier", "entity"]
        assert list(entity_errors_df.columns) == list(tier.entity_data_errors.columns)

        _assert_non_empty_csv(tier_output_folder / "group_data_errors.csv")
        group_errors_df = pd.read_csv(tier_output_folder / "group_data_errors.csv", index_col=["tier", "group"])
        assert list(group_errors_df.index.names) == ["tier", "group"]
        assert list(group_errors_df.columns) == list(tier.group_data_errors.columns)

        metadata = json.loads((tier_output_folder / "result_metadata.json").read_text(encoding="utf-8"))
        assert metadata["tier_name"] == tier_name
        assert metadata["species_name"] == multitier.species_name
        assert metadata["output_folder"] == str(tier_output_folder.resolve())
        assert metadata["tier_entities"] == tier.tier_entities
        assert metadata["tier_groups"] == tier.tier_groups
        assert metadata["tier_parameters"] == tier.tier_pars
        assert metadata["estimation_settings"] == tier.estimation_settings
        assert metadata["estimation_start_time"] is not None
        assert metadata["estimation_end_time"] is not None
        assert metadata["elapsed_duration_seconds"] is not None
        if len(tier.tier_entities) == 1:
            expected_iteration_count = 1
        elif len(tier.tier_groups):
            expected_iteration_count = len(tier.tier_groups)
        else:
            expected_iteration_count = len(tier.tier_entities)
        assert len(metadata["estimation_iterations"]) == expected_iteration_count
        assert all(iteration["estimation_start_time"] is not None for iteration in metadata["estimation_iterations"])
        assert all(iteration["estimation_end_time"] is not None for iteration in metadata["estimation_iterations"])
        assert all(iteration["elapsed_duration_seconds"] is not None for iteration in metadata["estimation_iterations"])

        summary = json.loads((tier_output_folder / "result_summary.json").read_text(encoding="utf-8"))
        assert summary["tier_name"] == tier_name
        assert summary["species_name"] == multitier.species_name
        assert summary["n_tier_entities"] == len(tier.tier_entities)
        assert summary["n_tier_groups"] == len(tier.tier_groups)
        assert summary["tier_parameters"] == tier.tier_pars
        assert summary["elapsed_duration_seconds"] == metadata["elapsed_duration_seconds"]
        expected_mean_parameters = {}
        for parameter_name in tier.tier_pars:
            parameter_mean = pd.to_numeric(tier.pars_df[parameter_name], errors="coerce").dropna().mean()
            expected_mean_parameters[parameter_name] = None if pd.isna(parameter_mean) else parameter_mean
        assert summary["mean_estimated_parameters"] == expected_mean_parameters
