import warnings
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import cast

import pandas as pd
from tabulate import tabulate

from ..estimation_files import (
    CopyFileTemplate,
    EstimationTemplates,
    RunSubstitutionTemplate,
)
from ..estimation_files.writer import write_tier_estimation_files
from . import results
from .estimation_files import MultitierGenerationContext
from .mydata import MultitierMyDataSubstitutionTemplate
from .pars_init import MultitierParsInitSubstitutionTemplate
from ..utils.entity_list import normalize_entity_list


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
      entities, groups, estimated parameters, estimation settings actually used, persisted timestamps, overall elapsed
      duration in seconds, and per-iteration timing records for each group or entity estimation performed within the
      tier. Per-iteration folders are persisted as ``relative_output_folder`` values relative to the tier result
      folder; machine-specific absolute paths are intentionally excluded from the schema.
    - ``result_summary.json`` stores a compact structured summary for quick inspection and loading. It includes:
      ``tier_name``, ``species_name``, ``n_tier_entities``, ``n_tier_groups``, ordered ``tier_parameters``,
      ``elapsed_duration_seconds``, ``mean_estimated_parameters`` as a parameter-to-mean mapping, and aggregated
      ``mean_entity_errors_by_tier`` / ``mean_group_errors_by_tier`` mappings for each tier at or below the current
      tier.

    Generated MATLAB files such as ``mydata_<species>.m``, ``pars_init_<species>.m``, ``predict_<species>.m``, and
    ``run_<species>.m`` may also exist in the tier folder or nested estimation subfolders. Those files are execution
    artifacts for the current workflow, not part of the stable result-file schema.
    """

    RESULT_METADATA_FILE = results.RESULT_METADATA_FILE
    RESULT_SUMMARY_FILE = results.RESULT_SUMMARY_FILE
    RESULT_SCHEMA_VERSION = results.RESULT_SCHEMA_VERSION
    OUTPUT_FILE_DESCRIPTIONS = results.OUTPUT_FILE_DESCRIPTIONS
    OUTPUT_FILES = results.OUTPUT_FILES

    def __init__(self, tier_structure, tier_name, tier_pars: list, template_folder: str | Path | None = None,
                 estimation_templates: EstimationTemplates | dict | None = None,
                 output_folder: str | Path = ".", extra_info="", extra_pseudo_data=None):
        if extra_pseudo_data is None:
            extra_pseudo_data = {}
        self.tier_structure = tier_structure
        self.name = tier_name
        self.tier_pars = tier_pars
        self.pars_df = None
        self.tier_entities = list(self.tier_structure.entity_hierarchy.get_entities(self.name))
        self.tier_groups = list(self.tier_structure.data[tier_name].groups)
        self.template_folder = Path(template_folder) if template_folder is not None else None
        if estimation_templates is not None:
            self.estimation_templates = EstimationTemplates.from_mapping(estimation_templates)
        elif template_folder is not None:
            species_name = self.tier_structure.species_name
            self.estimation_templates = EstimationTemplates(
                mydata=MultitierMyDataSubstitutionTemplate(
                    source=self.template_folder / f"mydata_{species_name}.m"
                ),
                pars_init=MultitierParsInitSubstitutionTemplate(
                    source=self.template_folder / f"pars_init_{species_name}.m"
                ),
                predict=CopyFileTemplate(self.template_folder / f"predict_{species_name}.m"),
                run=RunSubstitutionTemplate(
                    source=self.template_folder / f"run_{species_name}.m"
                ),
            )
        else:
            self.estimation_templates = None
        self.output_folder = Path(output_folder)
        self.estimation_settings = None
        self.pseudo_data = extra_pseudo_data
        self.extra_info = extra_info

        self.set_tier_parameters(tier_pars)

        # TODO: This should likely be part of a TieredDataCollection object to simplify these accesses
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
        # TODO: Need to make this generation deterministic, sort after generation

        self.entity_data_errors = pd.DataFrame(
            columns=list(entity_data_types),
            index=pd.MultiIndex.from_tuples(entity_list, names=("tier", "entity")),
        )
        self.group_data_errors = pd.DataFrame(
            columns=list(group_data_types),
            index=pd.MultiIndex.from_tuples(group_list, names=("tier", "group")),
        )

        self.estim_start_time = None
        self.estim_end_time = None
        self.estimation_iterations = []
        self.result_metadata = None
        self.result_summary = None
        self.initial_par_values = None

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
        self.initial_par_values = None

    def set_estimation_settings(self, estimation_settings):
        if estimation_settings is None:
            self.estimation_settings = None
            return

        self.estimation_settings = deepcopy(estimation_settings)

    def _normalize_initial_parameter_entities(self, entity_list):
        normalized_entity_list = normalize_entity_list(entity_list)
        if normalized_entity_list == "all":
            return list(self.tier_entities)
        return list(normalized_entity_list)

    def _normalize_explicit_initial_pars(self, initial_pars, entity_list):
        entity_list = self._normalize_initial_parameter_entities(entity_list)
        initial_values = pd.DataFrame(index=entity_list, columns=self.tier_pars, dtype=object)
        initial_values.index.name = "entity"
        if initial_pars is None:
            return initial_values

        if isinstance(initial_pars, pd.DataFrame):
            unknown_parameters = [parameter for parameter in initial_pars.columns if parameter not in self.tier_pars]
            if unknown_parameters:
                unknown_parameters_str = ", ".join(map(str, unknown_parameters))
                raise ValueError(
                    f"Initial parameters for tier '{self.name}' include unknown tier parameters: "
                    f"{unknown_parameters_str}."
                )
            missing_entities = [entity_id for entity_id in entity_list if entity_id not in initial_pars.index]
            if missing_entities:
                missing_entities_str = ", ".join(map(str, missing_entities))
                raise ValueError(
                    f"Initial parameters for tier '{self.name}' are missing entities: {missing_entities_str}."
                )
            for parameter_name in self.tier_pars:
                if parameter_name in initial_pars.columns:
                    initial_values.loc[entity_list, parameter_name] = initial_pars.loc[entity_list, parameter_name]
            return initial_values

        if not isinstance(initial_pars, Mapping):
            raise TypeError(
                "initial_pars must be None, a mapping of parameter values, or a pandas DataFrame."
            )

        unknown_parameters = [parameter for parameter in initial_pars if parameter not in self.tier_pars]
        if unknown_parameters:
            unknown_parameters_str = ", ".join(map(str, unknown_parameters))
            raise ValueError(
                f"Initial parameters for tier '{self.name}' include unknown tier parameters: "
                f"{unknown_parameters_str}."
            )

        for parameter_name, parameter_values in initial_pars.items():
            if isinstance(parameter_values, Mapping):
                missing_entities = [entity_id for entity_id in entity_list if entity_id not in parameter_values]
                if missing_entities:
                    missing_entities_str = ", ".join(map(str, missing_entities))
                    raise ValueError(
                        f"Initial parameter '{parameter_name}' for tier '{self.name}' is missing entities: "
                        f"{missing_entities_str}."
                    )
                for entity_id in entity_list:
                    initial_values.loc[entity_id, parameter_name] = parameter_values[entity_id]
            else:
                initial_values.loc[entity_list, parameter_name] = parameter_values
        return initial_values

    def _get_explicit_initial_value(self, explicit_initial_values, entity_id, parameter_name):
        value = explicit_initial_values.loc[entity_id, parameter_name]
        if pd.notna(value):
            return value
        return None

    def _get_pseudo_data_initial_value(self, entity_id, parameter_name):
        if isinstance(self.pseudo_data, pd.DataFrame):
            if parameter_name in self.pseudo_data.columns and entity_id in self.pseudo_data.index:
                value = self.pseudo_data.loc[entity_id, parameter_name]
                if pd.notna(value):
                    return value
            return None

        if isinstance(self.pseudo_data, Mapping) and parameter_name in self.pseudo_data:
            parameter_values = self.pseudo_data[parameter_name]
            if isinstance(parameter_values, Mapping):
                if entity_id not in parameter_values:
                    return None
                value = parameter_values[entity_id]
            else:
                value = parameter_values
            if pd.notna(value):
                return value
        return None

    def _get_parent_initial_value(self, entity_id, parameter_name):
        if self.tier_above is None:
            return None
        parent_tier = self.tier_structure.tiers[self.tier_above]
        parent_pars = parent_tier.pars_df
        parent_entity_id = self.tier_structure.entity_hierarchy.get_entity_at_tier(
            self.name,
            entity_id,
            self.tier_above,
        )
        if parameter_name not in parent_pars.columns or parent_entity_id not in parent_pars.index:
            return None
        value = parent_pars.loc[parent_entity_id, parameter_name]
        if pd.notna(value):
            return value
        return None

    def _get_base_initial_value(self, parameter_name):
        base_pars = getattr(self.tier_structure, "base_pars", None)
        if base_pars is None:
            base_pars = getattr(self.tier_structure, "pars", {})
        if parameter_name not in base_pars:
            return None
        value = base_pars[parameter_name]
        if pd.notna(value):
            return value
        return None

    def resolve_initial_parameter_values(self, initial_pars=None, entity_list="all"):
        entity_list = self._normalize_initial_parameter_entities(entity_list)
        explicit_initial_values = self._normalize_explicit_initial_pars(initial_pars, entity_list=entity_list)
        resolved_values = pd.DataFrame(index=entity_list, columns=self.tier_pars, dtype=object)
        resolved_values.index.name = "entity"

        for entity_id in entity_list:
            for parameter_name in self.tier_pars:
                value = self._get_explicit_initial_value(explicit_initial_values, entity_id, parameter_name)
                if value is None:
                    value = self._get_pseudo_data_initial_value(entity_id, parameter_name)
                if value is None:
                    value = self._get_parent_initial_value(entity_id, parameter_name)
                if value is None and self.tier_above is None:
                    value = self._get_base_initial_value(parameter_name)
                resolved_values.loc[entity_id, parameter_name] = value

        self._validate_initial_parameter_values(resolved_values)
        return resolved_values

    def _validate_initial_parameter_values(self, initial_values):
        missing = []
        for entity_id in initial_values.index:
            for parameter_name in initial_values.columns:
                if pd.isna(initial_values.loc[entity_id, parameter_name]):
                    missing.append(f"{parameter_name}@{entity_id}")
        if missing:
            missing_values = ", ".join(missing)
            raise ValueError(
                f"Initial parameter values for tier '{self.name}' are missing: {missing_values}."
            )

    def set_initial_parameter_values(self, initial_pars=None, entity_list="all"):
        self.initial_par_values = self.resolve_initial_parameter_values(
            initial_pars=initial_pars,
            entity_list=entity_list,
        )
        return self.initial_par_values

    def get_initial_parameter_values(self, entity_list="all"):
        entity_list = self._normalize_initial_parameter_entities(entity_list)
        if self.initial_par_values is None:
            return self.resolve_initial_parameter_values(entity_list=entity_list)
        missing_entities = [entity_id for entity_id in entity_list if entity_id not in self.initial_par_values.index]
        if missing_entities:
            missing_entities_str = ", ".join(map(str, missing_entities))
            raise ValueError(
                f"Initial parameter values for tier '{self.name}' have not been resolved for entities: "
                f"{missing_entities_str}."
            )
        return self.initial_par_values.loc[entity_list, self.tier_pars].copy()

    def get_initial_parameter_values_dict(self):
        if self.initial_par_values is None:
            return None
        return self.initial_par_values.to_dict()

    def estimate(self, pseudo_data_weight=0.1, save_results=True, print_results=True, hide_output=True,
                 estimation_settings=None, entity_list="all", trace_output=False,
                 print_pars_after_estimation=False, initial_pars=None):
        """

        :param pseudo_data_weight:
        :param save_results:
        :param print_results:
        :param hide_output:
        :param estimation_settings:
        :param entity_list:
        :param trace_output:
        :param print_pars_after_estimation:
        :param initial_pars:
        :return:
        """
        if estimation_settings is not None:
            self.set_estimation_settings(estimation_settings)
        if self.estimation_settings is None:
            raise ValueError(f"Estimation settings must be provided for tier '{self.name}' before estimation.")
        if self.estimation_templates is None:
            raise ValueError(f"Estimation templates must be provided for tier '{self.name}' before estimation.")

        self.estim_start_time = pd.Timestamp.now()
        self.estimation_iterations = []

        estimation_templates = self.estimation_templates
        estimation_targets = self.get_estimation_targets(entity_list=entity_list)
        total_iterations = len(estimation_targets)
        target_entities = []
        for estimation_target in estimation_targets:
            for target_entity_id in cast(list[str], estimation_target["entity_list"]):
                if target_entity_id not in target_entities:
                    target_entities.append(target_entity_id)
        self.set_initial_parameter_values(initial_pars=initial_pars, entity_list=target_entities)

        if trace_output:
            print(f"Tier {self.name} | start {self.estim_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        for iteration_index, estimation_target in enumerate(estimation_targets, start=1):
            group_name = cast(str, estimation_target["folder_name"])
            target_entity_list = list(cast(list[str], estimation_target["entity_list"]))
            target_type = cast(str, estimation_target["target_type"])
            target_name = cast(str, estimation_target["target_name"])
            target_entities_text = ", ".join(map(str, target_entity_list))
            iteration_start_time = pd.Timestamp.now()
            if trace_output:
                print(f"[{iteration_index}/{total_iterations}] {iteration_start_time.strftime('%H:%M:%S')} | {target_entities_text}")
            output_folder = self.output_folder / group_name
            output_folder.mkdir(parents=True, exist_ok=True)
            self.tier_structure.estimation_runner.estim_files_dir = output_folder
            generation_context = MultitierGenerationContext.from_tier_estimator(
                tier_estimator=self,
                entity_list=target_entity_list,
                pseudo_data_weight=pseudo_data_weight,
                output_folder=output_folder,
            )
            write_tier_estimation_files(estimation_templates, generation_context)

            success = self.tier_structure.estimation_runner.run_estimation(hide_output=hide_output)
            iteration_end_time = pd.Timestamp.now()
            if trace_output:
                if not success:
                    print(f"[{iteration_index}/{total_iterations}] {iteration_end_time.strftime('%H:%M:%S')} | FAIL")
            self.estimation_iterations.append(results.build_estimation_iteration_metadata(
                target_type=target_type,
                target_name=target_name,
                entity_list=target_entity_list,
                output_folder=output_folder,
                tier_output_folder=self.output_folder,
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

        if trace_output:
            print(f"Tier {self.name} | done {self.estim_end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        if print_results:
            self.print_results()
        if save_results:
            self.save_results()
        if print_pars_after_estimation:
            self.print_pars()

        return estimation_targets

    def get_estimation_targets(self, entity_list="all"):
        entity_list = normalize_entity_list(entity_list)
        if entity_list == "all":
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
            tier_output_folder=self.output_folder,
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
