import json
import shutil
from copy import deepcopy
from pathlib import Path
from string import Template

import pandas as pd
from tabulate import tabulate

from ..data_sources.collection import DataCollection
from ..estimation.runner import EstimationRunner
from .hierarchy import TierHierarchy
from ..utils.mydata_code_generation import check_files_exist_in_folder, generate_tier_variable_code, \
    generate_meta_data_code
from ..utils.data_conversion import convert_list_of_strings_to_matlab, convert_dict_to_matlab

class MultiTierStructure:
    def __init__(self, species_name: str, entity_hierarchy: TierHierarchy, data: dict[str, DataCollection], pars: dict,
                 tier_pars: dict, template_folder: str | Path, output_folder: str | Path, matlab_session='auto'):
        self.data = data
        self.species_name = species_name
        self.entity_hierarchy = entity_hierarchy
        self.tier_names = list(self.entity_hierarchy.tier_names)
        self.template_folder = Path(template_folder)
        self.output_folder = Path(output_folder)
        self.pars = pars
        self.tier_pars = tier_pars
        self.tiers = {}
        self.build_tiers()
        self.estimation_runner = EstimationRunner(estim_files_dir=self.output_folder, species_name=self.species_name,
                                                  matlab_session=matlab_session)

    def build_tiers(self):
        self.output_folder.mkdir(parents=True, exist_ok=True)
        # Save materialized path view of the hierarchy in output folder for reference
        self.entity_hierarchy.to_dataframe().to_csv(self.output_folder / "entity_vs_tier.csv")

        # Create estimators for each name
        for tier_name in self.tier_names:
            template_folder = self.template_folder / tier_name
            if not template_folder.is_dir():
                raise Exception(f"Template folder for tier {tier_name} not found at: {template_folder}")
            tier_pars_str = ' '.join(self.tier_pars[tier_name])
            if not all([p in self.pars for p in self.tier_pars[tier_name]]):
                raise Exception(f"Cannot estimate tier pars {tier_pars_str} for {tier_name} tier as they"
                                f" are not all estimated in the previous tier.")
            tier_output_folder = self.output_folder / tier_name

            tier_output_folder.mkdir(parents=True, exist_ok=True)
            self.tiers[tier_name] = TierEstimator(tier_structure=self,
                                                  tier_name=tier_name,
                                                  tier_pars=self.tier_pars[tier_name],
                                                  template_folder=template_folder,
                                                  output_folder=tier_output_folder)

    def get_pars_from_tier_above(self, tier_name):
        return self.tiers[self.entity_hierarchy.get_parent_tier(tier_name)].pars_df

    def get_init_par_values(self, tier_name, entity_list='all'):
        """
        Get initial values of tier parameters for a list of tier samples, based on previous estimates of parameters.
        If pseudo data are provided, then these are used as initial values.
        :param tier_name: Tier identifier.
        :param entity_list: List of tier samples.
        :return: a DataFrame with initial values of tier parameters for all tier samples.
        """
        if entity_list == 'all':
            entity_list = list(self.entity_hierarchy.get_entities(tier_name))
        init_par_values = pd.DataFrame(columns=self.tier_pars[tier_name], index=entity_list)

        prev_tier = self.entity_hierarchy.get_parent_tier(tier_name)
        # Case for top tier
        if prev_tier is None:
            for ts_id in entity_list:
                for par in self.tier_pars[tier_name]:
                    init_par_values.loc[ts_id, par] = self.pars[par]
        else:
            prev_tier_par_values = self.get_pars_from_tier_above(tier_name)
            for ts_id in entity_list:
                prev_ts_id = self.entity_hierarchy.get_entity_at_tier(tier_name, ts_id, prev_tier)
                for par in self.tier_pars[tier_name]:
                    # Use pseudo data if available
                    if par in self.tiers[tier_name].pseudo_data:
                        init_par_values.loc[ts_id, par] = self.tiers[tier_name].pseudo_data.loc[ts_id, par]
                    # Else use previous tier value
                    else:
                        init_par_values.loc[ts_id, par] = prev_tier_par_values.loc[prev_ts_id, par]

        return init_par_values

    def get_full_pars_dict(self, tier_name, entity_id, include_tier=False):
        """
        Get the values of all parameters in a given tier for a given entity. If include_tier is true,
        then the function returns the parameter values estimated for the tier tier_name. Otherwise, it returns the
        parameter values based only on higher tiers.
        :param tier_name:
        :param entity_id:
        :param include_tier:
        :return:
        """
        pars_dict = self.pars.copy()
        ts_tiers = self.entity_hierarchy.get_path(tier_name, entity_id)
        for t in self.tier_names:
            if self.entity_hierarchy.get_parent_tier(t) == tier_name:
                break
            if not include_tier and t == tier_name:
                continue
            for par in self.tier_pars[t]:
                pars_dict[par] = self.tiers[t].pars_df.loc[ts_tiers[t], par]
        return pars_dict

    def set_tier_parameters(self, tier_name, tier_pars):
        self.tier_pars[tier_name] = tier_pars
        self.tiers[tier_name].set_tier_parameters(tier_pars)


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

    Generated MATLAB files such as ``mydata_<species>.m``, ``pars_init_<species>.m``, ``predict_<species>.m``, and
    ``run_<species>.m`` may also exist in the tier folder or nested estimation subfolders. Those files are execution
    artifacts for the current workflow, not part of the stable result-file schema.
    """

    RESULT_METADATA_FILE = "result_metadata.json"
    RESULT_SCHEMA_VERSION = 1
    OUTPUT_FILE_DESCRIPTIONS = {
        "pars.csv": "Estimated tier parameters indexed by entity.",
        "entity_data_errors.csv": "Entity-level data errors indexed by tier and entity.",
        "group_data_errors.csv": "Group-level data errors indexed by tier and group.",
        RESULT_METADATA_FILE: "Tier result metadata and timing persisted as JSON.",
    }
    OUTPUT_FILES = list(OUTPUT_FILE_DESCRIPTIONS)

    def __init__(self, tier_structure: MultiTierStructure, tier_name, tier_pars: list, template_folder: str | Path,
                 output_folder: str | Path, extra_info='', extra_pseudo_data=None):
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
        # TODO: Extra info should be a dictionary with the data, and we should have a separate variable with the
        #  formatted version
        self.extra_info = extra_info

        self.set_tier_parameters(tier_pars)

        entity_list = []
        entity_data_types = set()
        group_list = []
        group_data_types = set()
        for tier_name in self.tier_structure.entity_hierarchy.get_all_tiers_below(self.name):
            # Entity data
            tier_entities = self.tier_structure.data[tier_name].entities
            entity_list.extend([(tier_name, entity_id) for entity_id in tier_entities])
            entity_data_types.update(self.tier_structure.data[tier_name].entity_data_types)
            # Group data
            tier_groups = self.tier_structure.data[tier_name].groups
            group_list.extend([(tier_name, g_id) for g_id in tier_groups])
            group_data_types.update(self.tier_structure.data[tier_name].group_data_types)

        self.entity_data_errors = pd.DataFrame(columns=list(entity_data_types),
                                               index=pd.MultiIndex.from_tuples(entity_list, names=('tier', 'entity')))
        self.group_data_errors = pd.DataFrame(columns=list(group_data_types),
                                              index=pd.MultiIndex.from_tuples(group_list, names=('tier', 'group')))

        self.code_generator = TierCodeGenerator(tier=self)
        self.estim_start_time = None
        self.estim_end_time = None
        self.estimation_iterations = []
        self.result_metadata = None

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
        self.pars_df.index.name = 'entity'

    def set_estimation_settings(self, estimation_settings):
        if estimation_settings is None:
            self.estimation_settings = None
            return

        self.estimation_settings = deepcopy(estimation_settings)

    def estimate(self, pseudo_data_weight=0.1, save_results=True, print_results=True, hide_output=True,
                 estimation_settings=None):
        if estimation_settings is not None:
            self.set_estimation_settings(estimation_settings)
        if self.estimation_settings is None:
            raise ValueError(f"Estimation settings must be provided for tier '{self.name}' before estimation.")

        print(f"Running estimation for {self.name} tier with parameters {' '.join(self.tier_pars)}.")
        self.estim_start_time = pd.Timestamp.now()
        self.estimation_iterations = []

        # TODO: Add option to only estimate for some tier samples not all that exist in the tier
        # Get list of tier samples or groups
        # If there is only one entity in the tier, then do not create a subfolder
        if len(self.tier_entities) == 1:
            estimation_targets = [{
                "target_type": "entity",
                "target_name": self.tier_entities[0],
                "folder_name": "",
                "entity_list": list(self.tier_entities),
            }]
        # Check if the tier has groups
        elif len(self.tier_groups):
            estimation_targets = [{
                "target_type": "group",
                "target_name": group_name,
                "folder_name": group_name,
                "entity_list": list(self.data.get_entity_list_of_group(group_name)),
            } for group_name in self.tier_groups]
        else:
            estimation_targets = [{
                "target_type": "entity",
                "target_name": entity_id,
                "folder_name": entity_id,
                "entity_list": [entity_id],
            } for entity_id in self.tier_entities]

        for estimation_target in estimation_targets:
            group_name = estimation_target["folder_name"]
            entity_list = estimation_target["entity_list"]
            iteration_start_time = pd.Timestamp.now()
            # Create estimation folder and set it in TierCodeGenerator and EstimationRunner objects
            output_folder = self.output_folder / group_name
            output_folder.mkdir(parents=True, exist_ok=True)
            self.tier_structure.estimation_runner.estim_files_dir = output_folder
            self.code_generator.output_folder = output_folder
            # Generate estimation files
            self.code_generator.generate_code(entity_list=entity_list, pseudo_data_weight=pseudo_data_weight)

            # Run estimation for name sample
            success = self.tier_structure.estimation_runner.run_estimation(hide_output=hide_output)
            iteration_end_time = pd.Timestamp.now()
            self.estimation_iterations.append(self.build_estimation_iteration_metadata(
                target_type=estimation_target["target_type"],
                target_name=estimation_target["target_name"],
                entity_list=entity_list,
                output_folder=output_folder,
                start_time=iteration_start_time,
                end_time=iteration_end_time,
                success=success,
            ))
            if not success:
                print(f"Estimation for {self.name} tier with parameters {' '.join(self.tier_pars)} failed for tier "
                      f"entity or group {estimation_target['target_name']}.")
                continue

            # Fetch and store results
            self.fetch_pars(entity_list=entity_list)
            self.fetch_errors()

        self.estim_end_time = pd.Timestamp.now()

        if print_results:
            self.print_results()
        if save_results:
            self.save_results()

    def fetch_pars(self, entity_list):
        pars = self.tier_structure.estimation_runner.fetch_pars_from_mat_file()
        # Store parameter values
        if len(self.pars_df) == 1:
            self.pars_df.iloc[0] = pars
        else:
            for par in self.tier_pars:
                for ts_id in entity_list:
                    self.pars_df.loc[ts_id, par] = pars[f'{par}_{ts_id}']

    def fetch_errors(self):
        estimation_errors = self.tier_structure.estimation_runner.fetch_errors_from_mat_file()

        for tier_name in self.tier_structure.entity_hierarchy.get_all_tiers_below(self.name):
            # Entity data
            tier = self.tier_structure.tiers[tier_name]
            for e_id in tier.data.entities:
                for dt in tier.data.entity_data_types:
                    varname = f'{dt}_{e_id}'
                    if varname in estimation_errors:
                        self.entity_data_errors.loc[(tier_name, e_id), dt] = estimation_errors[varname]
            # Group data
            for g_id in tier.data.groups:
                for dt in tier.data.group_data_types:
                    varname = f'{dt}_{g_id}'
                    if varname in estimation_errors:
                        self.group_data_errors.loc[(tier_name, g_id), dt] = estimation_errors[varname]

    @staticmethod
    def _serialize_metadata_value(value):
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if isinstance(value, dict):
            return {str(key): TierEstimator._serialize_metadata_value(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [TierEstimator._serialize_metadata_value(item) for item in value]
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

    @staticmethod
    def _deserialize_timestamp(value):
        if value in (None, ""):
            return None
        return pd.Timestamp(value)

    def get_elapsed_duration_seconds(self):
        if self.estim_start_time is None or self.estim_end_time is None:
            return None
        return (self.estim_end_time - self.estim_start_time).total_seconds()

    @staticmethod
    def get_duration_seconds(start_time, end_time):
        if start_time is None or end_time is None:
            return None
        return (end_time - start_time).total_seconds()

    def build_estimation_iteration_metadata(self, target_type, target_name, entity_list, output_folder,
                                            start_time, end_time, success):
        return self._serialize_metadata_value({
            "estimation_target_type": target_type,
            "estimation_target_name": target_name,
            "entity_list": list(entity_list),
            "output_folder": str(Path(output_folder).resolve()),
            "estimation_start_time": start_time,
            "estimation_end_time": end_time,
            "elapsed_duration_seconds": self.get_duration_seconds(start_time, end_time),
            "success": success,
        })

    def build_result_metadata(self):
        metadata = {
            "schema_version": self.RESULT_SCHEMA_VERSION,
            "stable_output_files": list(self.OUTPUT_FILES),
            "tier_name": self.name,
            "species_name": self.tier_structure.species_name,
            "output_folder": str(self.output_folder.resolve()),
            "tier_entities": list(self.tier_entities),
            "tier_groups": list(self.tier_groups),
            "tier_parameters": list(self.tier_pars),
            "estimation_settings": deepcopy(self.estimation_settings),
            "estimation_start_time": self.estim_start_time,
            "estimation_end_time": self.estim_end_time,
            "elapsed_duration_seconds": self.get_elapsed_duration_seconds(),
            "estimation_iterations": deepcopy(self.estimation_iterations),
        }
        return self._serialize_metadata_value(metadata)

    def _load_result_metadata(self):
        metadata_path = self.output_folder / self.RESULT_METADATA_FILE
        if not metadata_path.is_file():
            return None
        with metadata_path.open("r", encoding="utf-8") as metadata_file:
            return json.load(metadata_file)

    def _apply_result_metadata(self, metadata):
        metadata = deepcopy(metadata)
        if metadata.get("tier_name") not in (None, self.name):
            raise ValueError(
                f"Cannot load results for tier '{self.name}' from metadata for tier '{metadata['tier_name']}'."
            )
        if metadata.get("species_name") not in (None, self.tier_structure.species_name):
            raise ValueError(
                "Cannot load multitier results because the stored species name does not match the active "
                f"tier structure ('{metadata['species_name']}' != '{self.tier_structure.species_name}')."
            )

        self.result_metadata = metadata
        self.tier_entities = list(metadata.get("tier_entities", self.tier_entities))
        self.tier_groups = list(metadata.get("tier_groups", self.tier_groups))
        self.tier_pars = list(metadata.get("tier_parameters", self.tier_pars))
        self.estimation_settings = deepcopy(metadata.get("estimation_settings"))
        self.estim_start_time = self._deserialize_timestamp(metadata.get("estimation_start_time"))
        self.estim_end_time = self._deserialize_timestamp(metadata.get("estimation_end_time"))
        self.estimation_iterations = []
        for iteration in metadata.get("estimation_iterations", []):
            loaded_iteration = deepcopy(iteration)
            loaded_iteration["estimation_start_time"] = self._deserialize_timestamp(
                loaded_iteration.get("estimation_start_time")
            )
            loaded_iteration["estimation_end_time"] = self._deserialize_timestamp(
                loaded_iteration.get("estimation_end_time")
            )
            self.estimation_iterations.append(loaded_iteration)

    def save_results(self):
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.pars_df.to_csv(self.output_folder / "pars.csv")
        self.entity_data_errors.to_csv(self.output_folder / "entity_data_errors.csv")
        self.group_data_errors.to_csv(self.output_folder / "group_data_errors.csv")
        self.result_metadata = self.build_result_metadata()
        with (self.output_folder / self.RESULT_METADATA_FILE).open("w", encoding="utf-8") as metadata_file:
            json.dump(self.result_metadata, metadata_file, indent=2, sort_keys=True)

    def load_results(self):
        self.pars_df = pd.read_csv(self.output_folder / "pars.csv", index_col='entity')
        self.entity_data_errors = pd.read_csv(self.output_folder / "entity_data_errors.csv",
                                              index_col=['tier', 'entity'])
        self.group_data_errors = pd.read_csv(self.output_folder / "group_data_errors.csv",
                                             index_col=['tier', 'group'])
        self.tier_pars = list(self.pars_df.columns)
        self.tier_entities = list(self.pars_df.index)

        metadata = self._load_result_metadata()
        if metadata is None:
            self.result_metadata = None
            self.estimation_settings = None
            self.estim_start_time = None
            self.estim_end_time = None
            self.estimation_iterations = []
            return
        self._apply_result_metadata(metadata)

    def print_results(self):
        df = pd.concat([self.group_data_errors.groupby(level='tier').mean(),
                        self.entity_data_errors.groupby(level='tier').mean()], axis=1)
        print(tabulate(df, tablefmt="simple", showindex=True, headers="keys"))
        print('\n')

    def print_pars(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = self.tier_entities
        print(tabulate(self.pars_df.loc[entity_list, :], tablefmt="simple", showindex=True, headers="keys"))
        print('\n')


class TierCodeGenerator:
    FILES_NEEDED = ['mydata', 'pars_init', 'predict', 'run']

    def __init__(self, tier: TierEstimator):
        self.tier_estimator = tier
        self.tier_structure = tier.tier_structure
        self.output_folder = None

        complete, missing_file = self.check_all_files_exist(self.tier_estimator.template_folder)
        if not complete:
            raise Exception(f"Missing template file for tier {self.tier_estimator.name}: {missing_file}.")

    def check_all_files_exist(self, folder):
        files = [f"{tf}_{self.tier_estimator.tier_structure.species_name}.m" for tf in self.FILES_NEEDED]
        complete, missing_file = check_files_exist_in_folder(folder, files)
        return complete, missing_file

    def generate_mydata_file(self, entity_list, pseudo_data_weight=0.1):
        template_path = (
            self.tier_estimator.template_folder /
            f"mydata_{self.tier_estimator.tier_structure.species_name}.m"
        )
        output_path = self.output_folder / f"mydata_{self.tier_estimator.tier_structure.species_name}.m"

        entity_mydata_code_list = []
        group_mydata_code_list = []
        entity_data_types = set()
        group_data_types = set()
        tier_entities = {}
        tier_groups = {}
        tier_subtree = {entity_id: {} for entity_id in entity_list}
        groups_of_entity = {}
        for tier_name in self.tier_structure.entity_hierarchy.get_all_tiers_below(self.tier_estimator.name):
            tier = self.tier_structure.tiers[tier_name]

            # Get list of entities and groups to include in the estimation
            tier_entities_to_include = set()
            tier_groups_to_include = set()
            for entity_id in entity_list:
                te_list = self.tier_structure.entity_hierarchy.map_entities(
                    source_tier=self.tier_estimator.name, target_tier=tier_name, entity_list=[entity_id]
                )
                tier_entities_to_include.update(te_list)
                tier_groups_to_include.update(tier.data.get_group_list_from_entity_list(te_list))

                if tier_name != self.tier_estimator.name:
                    tier_subtree[entity_id][tier_name] = te_list

            # Generate mydata code
            ent_dt, ent_mc = tier.data.get_entity_mydata_code(tier_entities_to_include)
            entity_data_types.update(set(ent_dt))
            entity_mydata_code_list.extend(ent_mc)
            g_dt, g_mc = tier.data.get_group_mydata_code(tier_entities_to_include)
            group_data_types.update(set(g_dt))
            group_mydata_code_list.extend(g_mc)

            # Generate aux variables
            tier_entities[tier_name] = list(tier_entities_to_include)
            tier_groups[tier_name] = list(tier_groups_to_include)
            groups_of_entity.update(tier.data.get_groups_of_entities(tier_entities_to_include))

        entity_data_code = '\n'.join(entity_mydata_code_list)
        group_data_code = '\n'.join(group_mydata_code_list)

        entity_data_types_code = generate_meta_data_code(var_name='entity_data_types',
                                                         converted_data=convert_list_of_strings_to_matlab(
                                                             list(entity_data_types)))
        group_data_types_code = generate_meta_data_code(var_name='group_data_types',
                                                        converted_data=convert_list_of_strings_to_matlab(
                                                            list(group_data_types)))
        entity_list_code = generate_tier_variable_code(
            var_name='entity_list',
            converted_data=convert_list_of_strings_to_matlab(entity_list),
            label='List of entities',
            pars_init_access=True,
        )

        # List of entity ids per tier included in the estimation
        tier_entities_code = generate_tier_variable_code(
            var_name='tier_entities',
            converted_data=convert_dict_to_matlab(
                {t: convert_list_of_strings_to_matlab(g_list, double_brackets=True) for t, g_list in
                 tier_entities.items()}
            ),
            label='List of entity ids for each tier',
        )

        # List of group ids per tier included in the estimation
        tier_groups_code = generate_tier_variable_code(
            var_name='tier_groups',
            converted_data=convert_dict_to_matlab(
                {t: convert_list_of_strings_to_matlab(g_list, double_brackets=True) for t, g_list in
                 tier_groups.items()}
            ),
            label='List of groups ids for each tier',
        )

        # Subtree of hierarchical structure
        data_to_format = {}
        for entity_id, subtree in tier_subtree.items():
            data_to_format[entity_id] = convert_dict_to_matlab(
                {t: convert_list_of_strings_to_matlab(e_list, double_brackets=True) for t, e_list in subtree.items()})
        tier_subtree_code = generate_tier_variable_code(
            var_name='tier_subtree',
            converted_data=convert_dict_to_matlab(data_to_format),
            label='Tier subtree',
        )

        # Groups of entity
        groups_of_entity_code = generate_tier_variable_code(
            var_name='groups_of_entity',
            converted_data=convert_dict_to_matlab(
                {e_id: convert_list_of_strings_to_matlab(g_list, double_brackets=True) for e_id, g_list in
                 groups_of_entity.items()}
            ),
            label='Groups each entity belongs to'
        )

        # Tier parameters
        tier_pars_code = generate_tier_variable_code(
            var_name='tier_pars',
            converted_data=convert_list_of_strings_to_matlab(self.tier_estimator.tier_pars),
            label='Tier parameters',
            comment='Tier parameters',
            pars_init_access=True)

        # Initial values for tier parameters
        tier_par_init_values = self.tier_estimator.tier_structure.get_init_par_values(
            tier_name=self.tier_estimator.name, entity_list=entity_list).to_dict()
        tier_par_init_values_code = generate_meta_data_code(
            var_name='tier_par_init_values',
            converted_data=convert_dict_to_matlab(
                {p: convert_dict_to_matlab(init_values) for p, init_values in tier_par_init_values.items()})
        )

        with template_path.open('r') as mydata_template, output_path.open('w') as mydata_out:
            src = Template(mydata_template.read())
            result = src.substitute(
                entity_data=entity_data_code,
                group_data=group_data_code,
                entity_data_types=entity_data_types_code,
                group_data_types=group_data_types_code,
                entity_list=entity_list_code,
                tier_entities=tier_entities_code,
                tier_groups=tier_groups_code,
                tier_subtree=tier_subtree_code,
                groups_of_entity=groups_of_entity_code,
                tier_pars=tier_pars_code,
                tier_par_init_values=tier_par_init_values_code,
                extra_info=self.tier_estimator.extra_info,
                pseudo_data_weight=pseudo_data_weight
            )
            print(result, file=mydata_out)

    def generate_pars_init_file(self, entity_list):
        # TODO: Use multitier.ind_list_from_tier_sample_list()
        if entity_list == 'all':
            entity_list = list(self.tier_estimator.tier_structure.entity_hierarchy.get_entities(self.tier_estimator.name))
        pars_dict = self.tier_estimator.tier_structure.get_full_pars_dict(self.tier_estimator.name, entity_list[0])
        template_path = (
            self.tier_estimator.template_folder /
            f"pars_init_{self.tier_estimator.tier_structure.species_name}.m"
        )
        output_path = self.output_folder / f"pars_init_{self.tier_estimator.tier_structure.species_name}.m"

        with template_path.open('r') as pars_init_template, output_path.open('w') as pars_init_out:
            src = Template(pars_init_template.read())
            result = src.substitute(**pars_dict)
            print(result, file=pars_init_out)

    def generate_predict_file(self):
        shutil.copy(
            src=self.tier_estimator.template_folder / f"predict_{self.tier_estimator.tier_structure.species_name}.m",
            dst=self.output_folder)

    def generate_run_file(self):
        template_path = (
            self.tier_estimator.template_folder /
            f"run_{self.tier_estimator.tier_structure.species_name}.m"
        )
        output_path = self.output_folder / f"run_{self.tier_estimator.tier_structure.species_name}.m"
        with template_path.open('r') as run_template, output_path.open('w') as run_out:
            src = Template(run_template.read())
            result = src.substitute(self.tier_estimator.estimation_settings)
            print(result, file=run_out)

    def generate_code(self, entity_list, pseudo_data_weight=0.1):
        self.generate_mydata_file(entity_list=entity_list, pseudo_data_weight=pseudo_data_weight)
        self.generate_pars_init_file(entity_list=entity_list)
        self.generate_predict_file()
        self.generate_run_file()
