import json
from copy import deepcopy
from pathlib import Path

import pandas as pd


def serialize_metadata_value(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): serialize_metadata_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize_metadata_value(item) for item in value]
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return value.item()
        except (AttributeError, TypeError, ValueError):
            pass
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return value


def deserialize_timestamp(value):
    if value in (None, ""):
        return None
    return pd.Timestamp(value)


def get_duration_seconds(start_time, end_time):
    if start_time is None or end_time is None:
        return None
    return (end_time - start_time).total_seconds()


def get_elapsed_duration_seconds(tier_estimator):
    return get_duration_seconds(tier_estimator.estim_start_time, tier_estimator.estim_end_time)


def build_estimation_iteration_metadata(
        target_type,
        target_name,
        entity_list,
        output_folder,
        start_time,
        end_time,
        success,
):
    return serialize_metadata_value({
        "estimation_target_type": target_type,
        "estimation_target_name": target_name,
        "entity_list": list(entity_list),
        "output_folder": str(Path(output_folder).resolve()),
        "estimation_start_time": start_time,
        "estimation_end_time": end_time,
        "elapsed_duration_seconds": get_duration_seconds(start_time, end_time),
        "success": success,
    })


def build_result_metadata(tier_estimator):
    metadata = {
        "schema_version": tier_estimator.RESULT_SCHEMA_VERSION,
        "stable_output_files": list(tier_estimator.OUTPUT_FILES),
        "tier_name": tier_estimator.name,
        "species_name": tier_estimator.tier_structure.species_name,
        "output_folder": str(tier_estimator.output_folder.resolve()),
        "tier_entities": list(tier_estimator.tier_entities),
        "tier_groups": list(tier_estimator.tier_groups),
        "tier_parameters": list(tier_estimator.tier_pars),
        "estimation_settings": deepcopy(tier_estimator.estimation_settings),
        "estimation_start_time": tier_estimator.estim_start_time,
        "estimation_end_time": tier_estimator.estim_end_time,
        "elapsed_duration_seconds": get_elapsed_duration_seconds(tier_estimator),
        "estimation_iterations": deepcopy(tier_estimator.estimation_iterations),
    }
    return serialize_metadata_value(metadata)


def load_result_metadata(tier_estimator):
    metadata_path = tier_estimator.output_folder / tier_estimator.RESULT_METADATA_FILE
    if not metadata_path.is_file():
        return None
    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


def apply_result_metadata(tier_estimator, metadata):
    metadata = deepcopy(metadata)
    if metadata.get("tier_name") not in (None, tier_estimator.name):
        raise ValueError(
            f"Cannot load results for tier '{tier_estimator.name}' from metadata for tier "
            f"'{metadata['tier_name']}'."
        )
    if metadata.get("species_name") not in (None, tier_estimator.tier_structure.species_name):
        raise ValueError(
            "Cannot load multitier results because the stored species name does not match the active "
            f"tier structure ('{metadata['species_name']}' != '{tier_estimator.tier_structure.species_name}')."
        )

    tier_estimator.result_metadata = metadata
    tier_estimator.tier_entities = list(metadata.get("tier_entities", tier_estimator.tier_entities))
    tier_estimator.tier_groups = list(metadata.get("tier_groups", tier_estimator.tier_groups))
    tier_estimator.tier_pars = list(metadata.get("tier_parameters", tier_estimator.tier_pars))
    tier_estimator.estimation_settings = deepcopy(metadata.get("estimation_settings"))
    tier_estimator.estim_start_time = deserialize_timestamp(metadata.get("estimation_start_time"))
    tier_estimator.estim_end_time = deserialize_timestamp(metadata.get("estimation_end_time"))
    tier_estimator.estimation_iterations = []
    for iteration in metadata.get("estimation_iterations", []):
        loaded_iteration = deepcopy(iteration)
        loaded_iteration["estimation_start_time"] = deserialize_timestamp(
            loaded_iteration.get("estimation_start_time")
        )
        loaded_iteration["estimation_end_time"] = deserialize_timestamp(
            loaded_iteration.get("estimation_end_time")
        )
        tier_estimator.estimation_iterations.append(loaded_iteration)


def save_results(tier_estimator):
    tier_estimator.output_folder.mkdir(parents=True, exist_ok=True)
    tier_estimator.pars_df.to_csv(tier_estimator.output_folder / "pars.csv")
    tier_estimator.entity_data_errors.to_csv(tier_estimator.output_folder / "entity_data_errors.csv")
    tier_estimator.group_data_errors.to_csv(tier_estimator.output_folder / "group_data_errors.csv")
    tier_estimator.result_metadata = build_result_metadata(tier_estimator)
    with (tier_estimator.output_folder / tier_estimator.RESULT_METADATA_FILE).open("w", encoding="utf-8") as metadata_file:
        json.dump(tier_estimator.result_metadata, metadata_file, indent=2, sort_keys=True)


def load_results(tier_estimator):
    tier_estimator.pars_df = pd.read_csv(tier_estimator.output_folder / "pars.csv", index_col="entity")
    tier_estimator.entity_data_errors = pd.read_csv(
        tier_estimator.output_folder / "entity_data_errors.csv",
        index_col=["tier", "entity"],
    )
    tier_estimator.group_data_errors = pd.read_csv(
        tier_estimator.output_folder / "group_data_errors.csv",
        index_col=["tier", "group"],
    )
    tier_estimator.tier_pars = list(tier_estimator.pars_df.columns)
    tier_estimator.tier_entities = list(tier_estimator.pars_df.index)

    metadata = load_result_metadata(tier_estimator)
    if metadata is None:
        tier_estimator.result_metadata = None
        tier_estimator.estimation_settings = None
        tier_estimator.estim_start_time = None
        tier_estimator.estim_end_time = None
        tier_estimator.estimation_iterations = []
        return
    apply_result_metadata(tier_estimator, metadata)
