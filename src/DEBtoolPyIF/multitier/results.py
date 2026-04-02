import json
from copy import deepcopy
from pathlib import Path

import pandas as pd

from ..utils.entity_list import normalize_entity_list


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


def _get_normalized_relative_output_folder(output_folder, tier_output_folder):
    try:
        relative_path = Path(output_folder).resolve().relative_to(Path(tier_output_folder).resolve())
    except ValueError as exc:
        raise ValueError(
            f"Cannot persist iteration metadata outside tier output folder: '{output_folder}'."
        ) from exc
    return relative_path.as_posix()


def build_estimation_iteration_metadata(
        target_type,
        target_name,
        entity_list,
        output_folder,
        tier_output_folder,
        start_time,
        end_time,
        success,
):
    entity_list = normalize_entity_list(entity_list, allow_all=False)
    return serialize_metadata_value({
        "estimation_target_type": target_type,
        "estimation_target_name": target_name,
        "entity_list": list(entity_list),
        "relative_output_folder": _get_normalized_relative_output_folder(output_folder, tier_output_folder),
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


def _get_summary_tier_names(tier_estimator):
    return list(tier_estimator.tier_structure.entity_hierarchy.get_all_tiers_below(tier_estimator.name))


def _build_mean_error_columns(error_df, summary_tier_names, prefix):
    mean_columns = {}
    available_tiers = set()
    if isinstance(error_df.index, pd.MultiIndex) and "tier" in error_df.index.names:
        available_tiers = set(error_df.index.get_level_values("tier"))

    for tier_name in summary_tier_names:
        if tier_name not in available_tiers:
            mean_columns[tier_name] = None
            continue

        tier_errors = error_df.xs(tier_name, level="tier")
        numeric_errors = tier_errors.apply(pd.to_numeric, errors="coerce")
        flattened_errors = pd.Series(numeric_errors.to_numpy().ravel()).dropna()
        mean_columns[tier_name] = None if flattened_errors.empty else flattened_errors.mean()

    return mean_columns


def _build_parameter_summary_columns(tier_estimator):
    parameter_columns = {}
    numeric_pars_df = tier_estimator.pars_df.apply(pd.to_numeric, errors="coerce")
    for parameter_name in tier_estimator.tier_pars:
        if parameter_name not in numeric_pars_df.columns:
            parameter_columns[parameter_name] = None
            continue

        mean_value = numeric_pars_df[parameter_name].dropna().mean()
        parameter_columns[parameter_name] = None if pd.isna(mean_value) else mean_value

    return parameter_columns


def build_result_summary(tier_estimator):
    summary_tier_names = _get_summary_tier_names(tier_estimator)
    return serialize_metadata_value({
        "tier_name": tier_estimator.name,
        "species_name": tier_estimator.tier_structure.species_name,
        "n_tier_entities": len(tier_estimator.tier_entities),
        "n_tier_groups": len(tier_estimator.tier_groups),
        "tier_parameters": list(tier_estimator.tier_pars),
        "elapsed_duration_seconds": get_elapsed_duration_seconds(tier_estimator),
        "mean_estimated_parameters": _build_parameter_summary_columns(tier_estimator),
        "mean_entity_errors_by_tier": _build_mean_error_columns(
            tier_estimator.entity_data_errors,
            summary_tier_names=summary_tier_names,
            prefix="mean_entity_error",
        ),
        "mean_group_errors_by_tier": _build_mean_error_columns(
            tier_estimator.group_data_errors,
            summary_tier_names=summary_tier_names,
            prefix="mean_group_error",
        ),
    })


def load_result_metadata(tier_estimator):
    metadata_path = tier_estimator.output_folder / tier_estimator.RESULT_METADATA_FILE
    if not metadata_path.is_file():
        return None
    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


def apply_result_metadata(tier_estimator, metadata):
    metadata = deepcopy(metadata)
    schema_version = metadata.get("schema_version")
    if schema_version != tier_estimator.RESULT_SCHEMA_VERSION:
        raise ValueError(
            f"Cannot load result metadata schema version {schema_version!r}; expected "
            f"{tier_estimator.RESULT_SCHEMA_VERSION}."
        )
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
    tier_estimator.result_summary = build_result_summary(tier_estimator)
    with (tier_estimator.output_folder / tier_estimator.RESULT_METADATA_FILE).open("w", encoding="utf-8") as metadata_file:
        json.dump(tier_estimator.result_metadata, metadata_file, indent=2, sort_keys=True)
    with (tier_estimator.output_folder / tier_estimator.RESULT_SUMMARY_FILE).open("w", encoding="utf-8") as summary_file:
        json.dump(tier_estimator.result_summary, summary_file, indent=2, sort_keys=True)


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
    else:
        apply_result_metadata(tier_estimator, metadata)

    tier_estimator.result_summary = build_result_summary(tier_estimator)
