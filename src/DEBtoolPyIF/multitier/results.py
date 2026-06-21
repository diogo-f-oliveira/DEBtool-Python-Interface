import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..utils.entity_list import normalize_entity_list
from .hierarchy import TierHierarchy


RESULT_METADATA_FILE = "result_metadata.json"
RESULT_SUMMARY_FILE = "result_summary.json"
RESULT_SCHEMA_VERSION = 2
OUTPUT_FILE_DESCRIPTIONS = {
    "pars.csv": "Estimated tier parameters indexed by entity.",
    "entity_data_errors.csv": "Entity-level errors indexed by tier and entity.",
    "group_data_errors.csv": "Group-level errors indexed by tier and group.",
    RESULT_METADATA_FILE: "Tier result metadata and timing persisted as JSON.",
    RESULT_SUMMARY_FILE: "Compact structured tier summary persisted as JSON.",
}
OUTPUT_FILES = list(OUTPUT_FILE_DESCRIPTIONS)


@dataclass
class TierResult:
    name: str
    output_folder: Path
    species_name: str | None
    pars_df: pd.DataFrame
    entity_data_errors: pd.DataFrame
    group_data_errors: pd.DataFrame
    metadata: dict | None = None
    summary: dict | None = None

    @classmethod
    def from_folder(
            cls,
            output_folder: str | Path,
            tier_name: str | None = None,
            species_name: str | None = None,
            entity_hierarchy: TierHierarchy | None = None,
    ) -> "TierResult":
        output_folder = Path(output_folder)
        if not output_folder.is_dir():
            raise FileNotFoundError(f"Cannot load tier results; missing tier folder '{output_folder}'.")

        pars_df = _read_required_csv(output_folder / "pars.csv", index_col="entity")
        entity_data_errors = _read_required_csv(
            output_folder / "entity_data_errors.csv",
            index_col=["tier", "entity"],
        )
        group_data_errors = _read_required_csv(
            output_folder / "group_data_errors.csv",
            index_col=["tier", "group"],
        )

        metadata = _load_json_if_exists(output_folder / RESULT_METADATA_FILE)
        if metadata is not None:
            _validate_metadata(metadata, tier_name=tier_name, species_name=species_name)
            resolved_tier_name = metadata.get("tier_name") or tier_name or output_folder.name
            resolved_species_name = metadata.get("species_name") or species_name
        else:
            resolved_tier_name = tier_name or output_folder.name
            resolved_species_name = species_name

        result = cls(
            name=resolved_tier_name,
            output_folder=output_folder,
            species_name=resolved_species_name,
            pars_df=pars_df,
            entity_data_errors=entity_data_errors,
            group_data_errors=group_data_errors,
            metadata=metadata,
        )
        result.summary = _load_json_if_exists(output_folder / RESULT_SUMMARY_FILE)
        if result.summary is None and entity_hierarchy is not None:
            result.summary = build_tier_result_summary(result, entity_hierarchy)
        return result

    @property
    def tier_pars(self):
        if self.metadata is not None and self.metadata.get("tier_parameters"):
            return list(self.metadata["tier_parameters"])
        return list(self.pars_df.columns)

    @property
    def tier_entities(self):
        if self.metadata is not None and self.metadata.get("tier_entities"):
            return list(self.metadata["tier_entities"])
        return list(self.pars_df.index)

    @property
    def tier_groups(self):
        if self.metadata is not None and self.metadata.get("tier_groups") is not None:
            return list(self.metadata["tier_groups"])
        if isinstance(self.group_data_errors.index, pd.MultiIndex) and "group" in self.group_data_errors.index.names:
            return list(dict.fromkeys(self.group_data_errors.index.get_level_values("group")))
        return []

    @property
    def estimation_settings(self):
        if self.metadata is None:
            return None
        return deepcopy(self.metadata.get("estimation_settings"))

    @property
    def estim_start_time(self):
        if self.metadata is None:
            return None
        return deserialize_timestamp(self.metadata.get("estimation_start_time"))

    @property
    def estim_end_time(self):
        if self.metadata is None:
            return None
        return deserialize_timestamp(self.metadata.get("estimation_end_time"))

    @property
    def estimation_iterations(self):
        if self.metadata is None:
            return []
        loaded_iterations = []
        for iteration in self.metadata.get("estimation_iterations", []):
            loaded_iteration = deepcopy(iteration)
            loaded_iteration["estimation_start_time"] = deserialize_timestamp(
                loaded_iteration.get("estimation_start_time")
            )
            loaded_iteration["estimation_end_time"] = deserialize_timestamp(
                loaded_iteration.get("estimation_end_time")
            )
            loaded_iterations.append(loaded_iteration)
        return loaded_iterations


@dataclass
class MultiTierResults:
    output_folder: Path
    entity_hierarchy: TierHierarchy
    tiers: dict[str, TierResult]
    species_name: str | None = None

    @classmethod
    def from_folder(
            cls,
            output_folder: str | Path,
            species_name: str | None = None,
    ) -> "MultiTierResults":
        output_folder = Path(output_folder)
        hierarchy_path = output_folder / "entity_vs_tier.csv"
        if not hierarchy_path.is_file():
            raise FileNotFoundError(f"Cannot load multitier results; missing '{hierarchy_path}'.")

        entity_hierarchy = TierHierarchy.from_csv(hierarchy_path)
        tiers = {}
        resolved_species_name = species_name
        for tier_name in entity_hierarchy.tier_names:
            tier_result = TierResult.from_folder(
                output_folder=output_folder / tier_name,
                tier_name=tier_name,
                species_name=species_name,
                entity_hierarchy=entity_hierarchy,
            )
            tiers[tier_name] = tier_result
            if resolved_species_name is None and tier_result.species_name is not None:
                resolved_species_name = tier_result.species_name
            elif (
                    resolved_species_name is not None
                    and tier_result.species_name is not None
                    and tier_result.species_name != resolved_species_name
            ):
                raise ValueError(
                    "Cannot load multitier results because tier result species names are inconsistent "
                    f"('{tier_result.species_name}' != '{resolved_species_name}')."
                )

        return cls(
            output_folder=output_folder,
            entity_hierarchy=entity_hierarchy,
            tiers=tiers,
            species_name=resolved_species_name,
        )

    @property
    def tier_names(self):
        return list(self.entity_hierarchy.tier_names)


def _read_required_csv(path: Path, **read_csv_kwargs):
    if not path.is_file():
        raise FileNotFoundError(f"Cannot load tier results; missing required file '{path}'.")
    return pd.read_csv(path, **read_csv_kwargs)


def _load_json_if_exists(path: Path):
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as json_file:
        return json.load(json_file)


def _validate_metadata(metadata, tier_name=None, species_name=None):
    schema_version = metadata.get("schema_version")
    if schema_version != RESULT_SCHEMA_VERSION:
        raise ValueError(
            f"Cannot load result metadata schema version {schema_version!r}; expected "
            f"{RESULT_SCHEMA_VERSION}."
        )
    if tier_name is not None and metadata.get("tier_name") not in (None, tier_name):
        raise ValueError(
            f"Cannot load results for tier '{tier_name}' from metadata for tier "
            f"'{metadata['tier_name']}'."
        )
    if species_name is not None and metadata.get("species_name") not in (None, species_name):
        raise ValueError(
            "Cannot load multitier results because the stored species name does not match the requested "
            f"species name ('{metadata['species_name']}' != '{species_name}')."
        )


def build_tier_result_summary(tier_result: TierResult, entity_hierarchy: TierHierarchy):
    summary_tier_names = list(entity_hierarchy.get_all_tiers_below(tier_result.name))
    return serialize_metadata_value({
        "tier_name": tier_result.name,
        "species_name": tier_result.species_name,
        "n_tier_entities": len(tier_result.tier_entities),
        "n_tier_groups": len(tier_result.tier_groups),
        "tier_parameters": list(tier_result.tier_pars),
        "elapsed_duration_seconds": None if tier_result.metadata is None else tier_result.metadata.get(
            "elapsed_duration_seconds"
        ),
        "mean_estimated_parameters": _build_parameter_summary_columns(tier_result),
        "mean_entity_errors_by_tier": _build_mean_error_columns(
            tier_result.entity_data_errors,
            summary_tier_names=summary_tier_names,
            prefix="mean_entity_error",
        ),
        "mean_group_errors_by_tier": _build_mean_error_columns(
            tier_result.group_data_errors,
            summary_tier_names=summary_tier_names,
            prefix="mean_group_error",
        ),
    })


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
        "initial_parameter_values": tier_estimator.get_initial_parameter_values_dict(),
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
    initial_parameter_values = metadata.get("initial_parameter_values")
    if initial_parameter_values is None:
        tier_estimator.initial_par_values = None
    else:
        tier_estimator.initial_par_values = pd.DataFrame(initial_parameter_values)
        tier_estimator.initial_par_values.index.name = "entity"
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
    tier_result = TierResult.from_folder(
        output_folder=tier_estimator.output_folder,
        tier_name=tier_estimator.name,
        species_name=tier_estimator.tier_structure.species_name,
        entity_hierarchy=tier_estimator.tier_structure.entity_hierarchy,
    )
    tier_estimator.pars_df = tier_result.pars_df
    tier_estimator.entity_data_errors = tier_result.entity_data_errors
    tier_estimator.group_data_errors = tier_result.group_data_errors
    tier_estimator.tier_pars = tier_result.tier_pars
    tier_estimator.tier_entities = tier_result.tier_entities
    tier_estimator.tier_groups = tier_result.tier_groups

    if tier_result.metadata is None:
        tier_estimator.result_metadata = None
        tier_estimator.initial_par_values = None
        tier_estimator.estimation_settings = None
        tier_estimator.estim_start_time = None
        tier_estimator.estim_end_time = None
        tier_estimator.estimation_iterations = []
    else:
        tier_estimator.result_metadata = tier_result.metadata
        initial_parameter_values = tier_result.metadata.get("initial_parameter_values")
        if initial_parameter_values is None:
            tier_estimator.initial_par_values = None
        else:
            tier_estimator.initial_par_values = pd.DataFrame(initial_parameter_values)
            tier_estimator.initial_par_values.index.name = "entity"
        tier_estimator.estimation_settings = tier_result.estimation_settings
        tier_estimator.estim_start_time = tier_result.estim_start_time
        tier_estimator.estim_end_time = tier_result.estim_end_time
        tier_estimator.estimation_iterations = tier_result.estimation_iterations

    tier_estimator.result_summary = tier_result.summary or build_result_summary(tier_estimator)
