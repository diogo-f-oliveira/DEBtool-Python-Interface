from pathlib import Path

import pandas as pd
import pytest


ESTIMATION_RESULTS_CACHE = {}
GENERATED_MATLAB_FILE_PREFIXES = ("mydata", "pars_init", "predict", "run")


@pytest.fixture
def estimated_multitier(
    example_name,
    examples_root,
    import_example_data_module,
    import_example_tier_module,
    import_example_estimation_module,
    tmp_path_factory,
):
    cache_key = example_name
    if cache_key in ESTIMATION_RESULTS_CACHE:
        return ESTIMATION_RESULTS_CACHE[cache_key]

    pytest.importorskip("matlab.engine")

    data_module = import_example_data_module(example_name)
    tier_module = import_example_tier_module(example_name)
    estimation_module = import_example_estimation_module(example_name)

    output_folder = tmp_path_factory.mktemp(f"{example_name}_multitier_outputs")
    original_output_folder = tier_module.ESTIMATION_FOLDER
    tier_module.ESTIMATION_FOLDER = str(output_folder)

    try:
        data = data_module.load_data(str(examples_root / example_name / "data"))

        try:
            multitier = tier_module.create_tier_structure(data, matlab_session="auto")
        except Exception as exc:
            pytest.skip(f"MATLAB-backed estimation setup is unavailable: {exc}")

        estimation_module.run_multitier_estimation(
            multitier,
            estimation_settings=estimation_module.FAST_TEST_ESTIMATION_SETTINGS,
        )

        result = (multitier, Path(output_folder))
        ESTIMATION_RESULTS_CACHE[cache_key] = result
        return result
    finally:
        tier_module.ESTIMATION_FOLDER = original_output_folder


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

        for filename in ("pars.csv", "entity_data_errors.csv", "group_data_errors.csv"):
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
