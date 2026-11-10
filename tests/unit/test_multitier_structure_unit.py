import json

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from DEBtoolPyIF.multitier import MultiTierResults, TierHierarchy, TierResult
from DEBtoolPyIF.multitier.tier_estimation import TierEstimator


def _write_entity_hierarchy(output_folder, hierarchy):
    output_folder.mkdir(parents=True, exist_ok=True)
    hierarchy.to_dataframe().to_csv(output_folder / "entity_vs_tier.csv")


def _write_saved_tier(
        output_folder,
        tier_name,
        species_name,
        entities,
        parameters,
        groups=None,
        *,
        write_metadata=True,
        metadata_overrides=None,
):
    tier_folder = output_folder / tier_name
    tier_folder.mkdir(parents=True, exist_ok=True)
    groups = groups or []

    pars_df = pd.DataFrame(
        {
            parameter: [float(index + 1) for index, _ in enumerate(entities)]
            for parameter in parameters
        },
        index=pd.Index(entities, name="entity"),
    )
    pars_df.to_csv(tier_folder / "pars.csv")

    entity_errors = pd.DataFrame(
        {"obs": [0.1 for _ in entities]},
        index=pd.MultiIndex.from_tuples(
            [(tier_name, entity_id) for entity_id in entities],
            names=("tier", "entity"),
        ),
    )
    entity_errors.to_csv(tier_folder / "entity_data_errors.csv")

    group_errors = pd.DataFrame(
        {"group_obs": [0.2 for _ in groups]},
        index=pd.MultiIndex.from_tuples(
            [(tier_name, group_id) for group_id in groups],
            names=("tier", "group"),
        ),
    )
    group_errors.to_csv(tier_folder / "group_data_errors.csv")

    metadata = {
        "schema_version": TierEstimator.RESULT_SCHEMA_VERSION,
        "stable_output_files": list(TierEstimator.OUTPUT_FILES),
        "tier_name": tier_name,
        "species_name": species_name,
        "tier_entities": list(entities),
        "tier_groups": list(groups),
        "tier_parameters": list(parameters),
        "estimation_settings": {"results_output_mode": 0},
        "estimation_start_time": None,
        "estimation_end_time": None,
        "elapsed_duration_seconds": None,
        "estimation_iterations": [],
    }
    if metadata_overrides is not None:
        metadata.update(metadata_overrides)
    if write_metadata:
        (tier_folder / TierEstimator.RESULT_METADATA_FILE).write_text(
            json.dumps(metadata, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    summary = {
        "tier_name": tier_name,
        "species_name": metadata["species_name"],
        "n_tier_entities": len(entities),
        "n_tier_groups": len(groups),
        "tier_parameters": list(parameters),
        "elapsed_duration_seconds": None,
        "mean_estimated_parameters": {
            parameter: float(index + 1)
            for index, parameter in enumerate(parameters)
        },
        "mean_entity_errors_by_tier": {tier_name: 0.1},
        "mean_group_errors_by_tier": {tier_name: None if not groups else 0.2},
    }
    (tier_folder / TierEstimator.RESULT_SUMMARY_FILE).write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return pars_df, entity_errors, group_errors, metadata, summary


@pytest.fixture
def simple_hierarchy():
    return TierHierarchy.from_paths(
        tier_names=["breed", "diet"],
        paths=[
            {"breed": "male", "diet": "CTRL"},
            {"breed": "male", "diet": "TMR"},
        ],
    )


def test_multitier_results_from_folder_rebuilds_hierarchy_without_rewriting_csv(
    tmp_path,
    monkeypatch,
    simple_hierarchy,
):
    output_folder = tmp_path / "multitier"
    _write_entity_hierarchy(output_folder, simple_hierarchy)
    _write_saved_tier(output_folder, "breed", "Test_species", ["male"], ["par_a"])
    _write_saved_tier(output_folder, "diet", "Test_species", ["CTRL", "TMR"], ["par_a"])
    original_csv = (output_folder / "entity_vs_tier.csv").read_text(encoding="utf-8")
    original_to_csv = pd.DataFrame.to_csv

    def guarded_to_csv(self, path_or_buf=None, *args, **kwargs):
        if path_or_buf is not None and getattr(path_or_buf, "name", None) == "entity_vs_tier.csv":
            raise AssertionError("from_folder() must not rewrite entity_vs_tier.csv")
        return original_to_csv(self, path_or_buf, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "to_csv", guarded_to_csv)

    results = MultiTierResults.from_folder(
        output_folder=output_folder,
        species_name="Test_species",
    )

    assert results.tier_names == ["breed", "diet"]
    assert results.entity_hierarchy.entities == simple_hierarchy.entities
    assert results.entity_hierarchy.parents == simple_hierarchy.parents
    assert (output_folder / "entity_vs_tier.csv").read_text(encoding="utf-8") == original_csv


def test_multitier_results_from_folder_loads_all_tier_results(
    tmp_path,
    simple_hierarchy,
):
    species_name = "Test_species"
    output_folder = tmp_path / "multitier"
    _write_entity_hierarchy(output_folder, simple_hierarchy)
    expected_breed = _write_saved_tier(
        output_folder=output_folder,
        tier_name="breed",
        species_name=species_name,
        entities=["male"],
        parameters=["par_a", "par_b"],
    )
    expected_diet = _write_saved_tier(
        output_folder=output_folder,
        tier_name="diet",
        species_name=species_name,
        entities=["CTRL", "TMR"],
        parameters=["par_a"],
        groups=["diet_group"],
    )

    results = MultiTierResults.from_folder(
        output_folder=output_folder,
        species_name=species_name,
    )

    assert results.species_name == species_name
    assert results.tiers["breed"].tier_pars == ["par_a", "par_b"]
    assert results.tiers["diet"].tier_pars == ["par_a"]
    assert results.tiers["diet"].tier_groups == ["diet_group"]

    assert_frame_equal(results.tiers["breed"].pars_df, expected_breed[0], check_dtype=False)
    assert_frame_equal(results.tiers["diet"].pars_df, expected_diet[0], check_dtype=False)
    assert_frame_equal(results.tiers["diet"].entity_data_errors, expected_diet[1], check_dtype=False)
    assert_frame_equal(results.tiers["diet"].group_data_errors, expected_diet[2], check_dtype=False)
    assert results.tiers["breed"].metadata == expected_breed[3]
    assert results.tiers["diet"].metadata == expected_diet[3]
    assert results.tiers["breed"].summary == expected_breed[4]


def test_tier_result_from_folder_supports_missing_metadata_file(tmp_path):
    species_name = "Test_species"
    _write_saved_tier(
        output_folder=tmp_path,
        tier_name="breed",
        species_name=species_name,
        entities=["male"],
        parameters=["par_a"],
        write_metadata=False,
    )

    tier_result = TierResult.from_folder(
        output_folder=tmp_path / "breed",
        tier_name="breed",
        species_name=species_name,
    )

    assert tier_result.metadata is None
    assert tier_result.name == "breed"
    assert tier_result.species_name == species_name
    assert tier_result.tier_pars == ["par_a"]
    assert tier_result.tier_entities == ["male"]
    assert tier_result.estimation_settings is None


def test_tier_result_from_folder_rejects_unsupported_metadata_schema(tmp_path):
    _write_saved_tier(
        output_folder=tmp_path,
        tier_name="breed",
        species_name="Test_species",
        entities=["male"],
        parameters=["par_a"],
        metadata_overrides={"schema_version": 1},
    )

    with pytest.raises(ValueError, match="schema version 1"):
        TierResult.from_folder(
            output_folder=tmp_path / "breed",
            tier_name="breed",
            species_name="Test_species",
        )


def test_tier_result_from_folder_rejects_tier_and_species_mismatches(tmp_path):
    _write_saved_tier(
        output_folder=tmp_path,
        tier_name="breed",
        species_name="Test_species",
        entities=["male"],
        parameters=["par_a"],
    )

    with pytest.raises(ValueError, match="metadata for tier 'breed'"):
        TierResult.from_folder(
            output_folder=tmp_path / "breed",
            tier_name="diet",
            species_name="Test_species",
        )

    with pytest.raises(ValueError, match="stored species name does not match"):
        TierResult.from_folder(
            output_folder=tmp_path / "breed",
            tier_name="breed",
            species_name="Other_species",
        )


def test_multitier_results_from_folder_fails_for_missing_required_files(tmp_path, simple_hierarchy):
    output_folder = tmp_path / "multitier"
    _write_entity_hierarchy(output_folder, simple_hierarchy)
    _write_saved_tier(output_folder, "breed", "Test_species", ["male"], ["par_a"])
    (output_folder / "diet").mkdir()

    with pytest.raises(FileNotFoundError, match="pars.csv"):
        MultiTierResults.from_folder(output_folder=output_folder, species_name="Test_species")
