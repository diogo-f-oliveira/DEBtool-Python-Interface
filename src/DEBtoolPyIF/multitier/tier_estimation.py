import warnings
from copy import deepcopy
from pathlib import Path

import pandas as pd
from tabulate import tabulate

from . import results
from .codegen import TierCodeGenerator


class TierEstimator:
    """
    Per-tier output contract after an estimation run.

    Stable machine-readable result files written directly in each tier output folder:
    - ``pars.csv`` stores estimated tier parameters indexed by entity. This remains unchanged for backward
      compatibility.
    - ``entity_data_errors.csv`` stores entity-level data errors for this tier and descendant tiers, indexed by
      ``(tier, entity)``. This remains unchanged for backward compatibility.
    - ``group_data_errors.csv`` stores group-level data errors for this tier and descendant tiers, indexed by
      ``(tier, group)``. This remains unchanged for backward compatibility.
    - ``result_metadata.json`` stores stable tier metadata for machine-readable loading, including tier identity,
      output folder, entities, groups, estimated parameters, estimation settings actually used, persisted timestamps,
      overall elapsed duration in seconds, and per-iteration timing records for each group or entity estimation
      performed within the tier.
    - ``result_summary.json`` stores a compact structured summary for quick inspection and loading. It includes:
      ``tier_name``, ``species_name``, ``n_tier_entities``, ``n_tier_groups``, ordered ``tier_parameters``,
      ``elapsed_duration_seconds``, ``mean_estimated_parameters`` as a parameter-to-mean mapping, and aggregated
      ``mean_entity_errors_by_tier`` / ``mean_group_errors_by_tier`` mappings for each tier at or below the current
      tier.

    Generated MATLAB files such as ``mydata_<species>.m``, ``pars_init_<species>.m``, ``predict_<species>.m``, and
    ``run_<species>.m`` may also exist in the tier folder or nested estimation subfolders. Those files are execution
    artifacts for the current workflow, not part of the stable result-file schema.
    """

    RESULT_METADATA_FILE = "result_metadata.json"
    RESULT_SUMMARY_FILE = "result_summary.json"
    RESULT_SCHEMA_VERSION = 1
    OUTPUT_FILE_DESCRIPTIONS = {
        "pars.csv": "Estimated tier parameters indexed by entity.",
        "entity_data_errors.csv": "Entity-level data errors indexed by tier and entity.",
        "group_data_errors.csv": "Group-level data errors indexed by tier and group.",
        RESULT_METADATA_FILE: "Tier result metadata and timing persisted as JSON.",
        RESULT_SUMMARY_FILE: "Compact structured tier summary persisted as JSON.",
    }
    OUTPUT_FILES = list(OUTPUT_FILE_DESCRIPTIONS)

    def __init__(self, tier_structure, tier_name, tier_pars: list, template_folder: str | Path,
                 output_folder: str | Path, extra_info="", extra_pseudo_data=None):
        if extra_pseudo_data is None:
            extra_pseudo_data = {}
        self.tier_structure = tier_structure
        self.name = tier_name
        self.tier_pars = tier_pars
        self.pars_df = None
        self.tier_entities = list(self.tier_structure.entity_hierarchy.get_entities(self.name))
        self.tier_groups = list(self.tier_structure.data[tier_name].groups)
        self.template_folder = Path(template_folder)
        self.output_folder = Path(output_folder)
        self.estimation_settings = None
        self.pseudo_data = extra_pseudo_data
        self.extra_info = extra_info

        self.set_tier_parameters(tier_pars)

        entity_list = []
        entity_data_types = set()
        group_list = []
        group_data_types = set()
        for child_tier_name in self.tier_structure.entity_hierarchy.get_all_tiers_below(self.name):
            tier = self.tier_structure.data[child_tier_name]
            tier_entities = tier.entities
            entity_list.extend([(child_tier_name, entity_id) for entity_id in tier_entities])
            entity_data_types.update(tier.entity_data_types)
            tier_groups = tier.groups
            group_list.extend([(child_tier_name, group_id) for group_id in tier_groups])
            group_data_types.update(tier.group_data_types)

        self.entity_data_errors = pd.DataFrame(
            columns=list(entity_data_types),
            index=pd.MultiIndex.from_tuples(entity_list, names=("tier", "entity")),
        )
        self.group_data_errors = pd.DataFrame(
            columns=list(group_data_types),
            index=pd.MultiIndex.from_tuples(group_list, names=("tier", "group")),
        )

        self.code_generator = TierCodeGenerator(tier=self)
        self.estim_start_time = None
        self.estim_end_time = None
        self.estimation_iterations = []
        self.result_metadata = None
        self.result_summary = None

    @property
    def data(self):
        return self.tier_structure.data[self.name]

    @property
    def tier_index(self):
        return self.tier_structure.entity_hierarchy.get_tier_index(self.name)

    @property
    def tier_below(self):
        return self.tier_structure.entity_hierarchy.get_child_tier(self.name)

    @property
    def tier_above(self):
        return self.tier_structure.entity_hierarchy.get_parent_tier(self.name)

    @property
    def estimation_complete(self):
        return self.pars_df.notna().all().all()

    def set_tier_parameters(self, tier_pars):
        self.tier_pars = tier_pars
        self.pars_df = pd.DataFrame(columns=self.tier_pars, index=self.tier_entities)
        self.pars_df.index.name = "entity"

    def set_estimation_settings(self, estimation_settings):
        if estimation_settings is None:
            self.estimation_settings = None
            return

        self.estimation_settings = deepcopy(estimation_settings)

    def estimate(self, pseudo_data_weight=0.1, save_results=True, print_results=True, hide_output=True,
                 estimation_settings=None, entity_list="all"):
        if estimation_settings is not None:
            self.set_estimation_settings(estimation_settings)
        if self.estimation_settings is None:
            raise ValueError(f"Estimation settings must be provided for tier '{self.name}' before estimation.")

        print(f"Running estimation for {self.name} tier with parameters {' '.join(self.tier_pars)}.")
        self.estim_start_time = pd.Timestamp.now()
        self.estimation_iterations = []

        estimation_targets = self.get_estimation_targets(entity_list=entity_list)

        for estimation_target in estimation_targets:
            group_name = estimation_target["folder_name"]
            target_entity_list = estimation_target["entity_list"]
            iteration_start_time = pd.Timestamp.now()
            output_folder = self.output_folder / group_name
            output_folder.mkdir(parents=True, exist_ok=True)
            self.tier_structure.estimation_runner.estim_files_dir = output_folder
            self.code_generator.output_folder = output_folder
            self.code_generator.generate_code(entity_list=target_entity_list, pseudo_data_weight=pseudo_data_weight)

            success = self.tier_structure.estimation_runner.run_estimation(hide_output=hide_output)
            iteration_end_time = pd.Timestamp.now()
            self.estimation_iterations.append(results.build_estimation_iteration_metadata(
                target_type=estimation_target["target_type"],
                target_name=estimation_target["target_name"],
                entity_list=target_entity_list,
                output_folder=output_folder,
                start_time=iteration_start_time,
                end_time=iteration_end_time,
                success=success,
            ))
            if not success:
                print(f"Estimation for {self.name} tier with parameters {' '.join(self.tier_pars)} failed for tier "
                      f"entity or group {estimation_target['target_name']}.")
                continue

            self.fetch_pars(entity_list=target_entity_list)
            self.fetch_errors()

        self.estim_end_time = pd.Timestamp.now()

        if print_results:
            self.print_results()
        if save_results:
            self.save_results()

    def get_estimation_targets(self, entity_list="all"):
        if entity_list in (None, "all"):
            requested_entities = list(self.tier_entities)
        else:
            requested_entities = list(dict.fromkeys(entity_list))
            invalid_entities = [entity_id for entity_id in requested_entities if entity_id not in self.tier_entities]
            if invalid_entities:
                invalid_entities_str = ", ".join(invalid_entities)
                raise ValueError(
                    f"Cannot estimate tier '{self.name}' for unknown entities: {invalid_entities_str}."
                )
            if not requested_entities:
                raise ValueError(f"Cannot estimate tier '{self.name}' with an empty entity list.")

        if len(self.tier_entities) == 1:
            return [{
                "target_type": "entity",
                "target_name": self.tier_entities[0],
                "folder_name": "",
                "entity_list": list(requested_entities),
            }]

        estimation_targets = []
        grouped_entities = set()
        requested_entities_set = set(requested_entities)

        for group_name in self.tier_groups:
            grouped_entity_list = list(self.data.get_entity_list_of_group(group_name))
            if not requested_entities_set.intersection(grouped_entity_list):
                continue

            requested_group_entities = [entity_id for entity_id in grouped_entity_list if entity_id in requested_entities_set]
            additional_group_entities = [
                entity_id for entity_id in grouped_entity_list if entity_id not in requested_entities_set
            ]
            if additional_group_entities:
                additional_entities_str = ", ".join(additional_group_entities)
                requested_entities_str = ", ".join(requested_group_entities)
                warnings.warn(
                    f"Requested estimation for {requested_entities_str} in group '{group_name}' also requires "
                    f"estimating other entities in that group: {additional_entities_str}.",
                    UserWarning,
                    stacklevel=2,
                )

            estimation_targets.append({
                "target_type": "group",
                "target_name": group_name,
                "folder_name": group_name,
                "entity_list": grouped_entity_list,
            })
            grouped_entities.update(grouped_entity_list)

        ungrouped_entities = [
            entity_id for entity_id in requested_entities
            if entity_id not in grouped_entities
        ]
        estimation_targets.extend([{
            "target_type": "entity",
            "target_name": entity_id,
            "folder_name": entity_id,
            "entity_list": [entity_id],
        } for entity_id in ungrouped_entities])

        return estimation_targets

    def fetch_pars(self, entity_list):
        pars = self.tier_structure.estimation_runner.fetch_pars_from_mat_file()
        if len(self.pars_df) == 1:
            self.pars_df.iloc[0] = pars
        else:
            for par in self.tier_pars:
                for ts_id in entity_list:
                    self.pars_df.loc[ts_id, par] = pars[f"{par}_{ts_id}"]

    def fetch_errors(self):
        estimation_errors = self.tier_structure.estimation_runner.fetch_errors_from_mat_file()

        for tier_name in self.tier_structure.entity_hierarchy.get_all_tiers_below(self.name):
            tier = self.tier_structure.tiers[tier_name]
            for entity_id in tier.data.entities:
                for data_type in tier.data.entity_data_types:
                    varname = f"{data_type}_{entity_id}"
                    if varname in estimation_errors:
                        self.entity_data_errors.loc[(tier_name, entity_id), data_type] = estimation_errors[varname]
            for group_id in tier.data.groups:
                for data_type in tier.data.group_data_types:
                    varname = f"{data_type}_{group_id}"
                    if varname in estimation_errors:
                        self.group_data_errors.loc[(tier_name, group_id), data_type] = estimation_errors[varname]

    @staticmethod
    def _serialize_metadata_value(value):
        return results.serialize_metadata_value(value)

    @staticmethod
    def _deserialize_timestamp(value):
        return results.deserialize_timestamp(value)

    def get_elapsed_duration_seconds(self):
        return results.get_elapsed_duration_seconds(self)

    @staticmethod
    def get_duration_seconds(start_time, end_time):
        return results.get_duration_seconds(start_time, end_time)

    def build_estimation_iteration_metadata(self, target_type, target_name, entity_list, output_folder,
                                            start_time, end_time, success):
        return results.build_estimation_iteration_metadata(
            target_type=target_type,
            target_name=target_name,
            entity_list=entity_list,
            output_folder=output_folder,
            start_time=start_time,
            end_time=end_time,
            success=success,
        )

    def build_result_metadata(self):
        return results.build_result_metadata(self)

    def build_result_summary(self):
        return results.build_result_summary(self)

    def _load_result_metadata(self):
        return results.load_result_metadata(self)

    def _apply_result_metadata(self, metadata):
        results.apply_result_metadata(self, metadata)

    def save_results(self):
        results.save_results(self)

    def load_results(self):
        results.load_results(self)

    def print_results(self):
        df = pd.concat([self.group_data_errors.groupby(level="tier").mean(),
                        self.entity_data_errors.groupby(level="tier").mean()], axis=1)
        print(tabulate(df, tablefmt="simple", showindex=True, headers="keys"))
        print("\n")

    def print_pars(self, entity_list="all"):
        if entity_list == "all":
            entity_list = self.tier_entities
        print(tabulate(self.pars_df.loc[entity_list, :], tablefmt="simple", showindex=True, headers="keys"))
        print("\n")
