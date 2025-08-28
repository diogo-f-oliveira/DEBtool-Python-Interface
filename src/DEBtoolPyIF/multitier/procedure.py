import pandas as pd
from string import Template
import os
import shutil
from tabulate import tabulate

from ..data_sources.collection import DataCollection
from ..estimation.runner import EstimationRunner
from ..utils.mydata_code_generation import check_files_exist_in_folder, format_list_of_strings_in_matlab, format_dict_in_matlab, \
    generate_tier_variable_code, generate_meta_data_code


class MultiTierStructure:
    def __init__(self, species_name: str, entity_vs_tier: pd.DataFrame, data: dict[str, DataCollection], pars: dict,
                 tier_pars: dict, template_folders: dict, output_folder: str, estimation_settings: dict,
                 tier_output_folders: dict, matlab_session=None):
        self.data = data
        self.species_name = species_name
        self.entity_vs_tier = entity_vs_tier
        self.tier_names = list(self.entity_vs_tier.columns)
        self.output_folder = output_folder
        self.pars = pars
        self.tier_pars = tier_pars
        self.tiers = {}
        self.build_tiers(estimation_settings=estimation_settings, template_folders=template_folders,
                         tier_output_folders=tier_output_folders)
        self.estimation_runner = EstimationRunner(estim_files_dir=self.output_folder, species_name=self.species_name,
                                                  matlab_session=matlab_session)

    def build_tiers(self, estimation_settings, template_folders, tier_output_folders):

        # Create estimators for each name
        for tier_name in self.tier_names:
            if tier_name not in template_folders:
                raise Exception(f"Template folder for name {tier_name} is not defined.")
            tier_pars_str = ' '.join(self.tier_pars[tier_name])
            if not all([p in self.pars for p in self.tier_pars[tier_name]]):
                raise Exception(f"Cannot estimate tier pars {tier_pars_str} for {tier_name} tier as they"
                                f" are not all estimated in the previous tier.")
            # Create output folder for name estimation
            if tier_name not in tier_output_folders:
                tier_output_folder = f"{self.output_folder}/{tier_name}"
            else:
                tier_output_folder = f"{self.output_folder}/{tier_output_folders[tier_name]}"

            os.makedirs(tier_output_folder, exist_ok=True)
            self.tiers[tier_name] = TierEstimator(tier_structure=self,
                                                  tier_name=tier_name,
                                                  tier_pars=self.tier_pars[tier_name],
                                                  template_folder=template_folders[tier_name],
                                                  output_folder=tier_output_folder,
                                                  estimation_settings=estimation_settings[tier_name])

    def get_all_entities_in_tier(self, tier_name):
        return self.entity_vs_tier.loc[tier_name].index.to_list()

    def entities_in_tier_below_from_entity_list(self, tier_name, tier_below, entity_list='all'):
        entities_of_tier_below = self.entity_vs_tier.loc[tier_below, tier_name]
        if entity_list == 'all':
            return entities_of_tier_below.index.to_list()
        return entities_of_tier_below[entities_of_tier_below.isin(entity_list)].index.to_list()

    def get_tier_index(self, tier_name):
        return self.tier_names.index(tier_name)

    def get_tier_above(self, tier_name):
        if tier_name == self.tier_names[0]:
            return None
        return self.tier_names[self.get_tier_index(tier_name) - 1]

    def get_tier_below(self, tier_name):
        if tier_name == self.tier_names[-1]:
            return None
        return self.tier_names[self.get_tier_index(tier_name) + 1]

    def get_all_tiers_below(self, tier_name):
        return self.tier_names[self.get_tier_index(tier_name):]

    def get_pars_from_tier_above(self, tier_name):
        return self.tiers[self.get_tier_above(tier_name)].pars_df

    def get_init_par_values(self, tier_name, entity_list='all'):
        """
        Get initial values of tier parameters for a list of tier samples, based on previous estimates of parameters.
        If pseudo data are provided, then these are used as initial values.
        :param tier_name: Tier identifier.
        :param entity_list: List of tier samples.
        :return: a DataFrame with initial values of tier parameters for all tier samples.
        """
        if entity_list == 'all':
            entity_list = self.get_all_entities_in_tier(tier_name)
        init_par_values = pd.DataFrame(columns=self.tier_pars[tier_name], index=entity_list)

        prev_tier = self.get_tier_above(tier_name)
        # Case for top tier
        if prev_tier is None:
            for ts_id in entity_list:
                for par in self.tier_pars[tier_name]:
                    init_par_values.loc[ts_id, par] = self.pars[par]
        else:
            prev_tier_par_values = self.get_pars_from_tier_above(tier_name)
            for ts_id in entity_list:
                prev_ts_id = self.entity_vs_tier.groupby(tier_name).get_group(ts_id)[prev_tier].iloc[0]
                for par in self.tier_pars[tier_name]:
                    # Use pseudo data if available
                    if par in self.tiers[tier_name].pseudo_data:
                        init_par_values.loc[ts_id, par] = self.tiers[tier_name].pseudo_data.loc[ts_id, par]
                    # Else use previous tier value
                    else:
                        init_par_values.loc[ts_id, par] = prev_tier_par_values.loc[prev_ts_id, par]

        return init_par_values

    def get_full_pars_dict(self, tier_name, tier_sample, include_tier=False):
        """
        Get the values of all parameters in a given tier for a given tier sample. If include_tier is true,
        then the function returns the parameter values estimated for the tier tier_name. Otherwise, it returns the
        parameter values based only on higher tiers.
        :param tier_name:
        :param tier_sample:
        :param include_tier:
        :return:
        """
        pars_dict = self.pars.copy()
        ts_tiers = self.entity_vs_tier.groupby(tier_name).get_group(tier_sample).iloc[0]
        for t in self.tier_names:
            if self.get_tier_above(t) == tier_name:
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
    OUTPUT_FILES = ['pars', 'ind_data_errors', 'group_data_errors', 'tier_errors']

    def __init__(self, tier_structure: MultiTierStructure, tier_name, tier_pars: list, template_folder: str,
                 output_folder: str, estimation_settings: dict, extra_info='', extra_pseudo_data=None):
        if extra_pseudo_data is None:
            extra_pseudo_data = {}
        self.tier_structure = tier_structure
        self.name = tier_name
        self.tier_pars = tier_pars
        self.pars_df = None
        self.tier_entities = self.tier_structure.get_all_entities_in_tier(self.name)
        self.tier_groups = list(self.tier_structure.data[tier_name].groups)
        self.template_folder = template_folder
        self.output_folder = output_folder
        self.estimation_settings = estimation_settings
        self.pseudo_data = extra_pseudo_data
        # TODO: Extra info should be a dictionary with the data, and we should have a separate variable with the
        #  formatted version
        self.extra_info = extra_info

        self.set_tier_parameters(tier_pars)

        entity_list = []
        entity_data_types = set()
        group_list = []
        group_data_types = set()
        for tier_name in self.tier_structure.get_all_tiers_below(self.name):
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

    @property
    def data(self):
        return self.tier_structure.data[self.name]

    @property
    def tier_index(self):
        return self.tier_structure.get_tier_index(self.name)

    @property
    def tier_below(self):
        return self.tier_structure.get_tier_below(self.name)

    @property
    def tier_above(self):
        return self.tier_structure.get_tier_above(self.name)

    @property
    def estimation_complete(self):
        return self.pars_df.notna().all().all()

    def set_tier_parameters(self, tier_pars):
        self.tier_pars = tier_pars
        self.pars_df = pd.DataFrame(columns=self.tier_pars, index=self.tier_entities)
        self.pars_df.index.name = 'entity'

    def estimate(self, pseudo_data_weight=0.1, save_results=True, print_results=True, hide_output=True):
        print(f"Running estimation for {self.name} tier with parameters {' '.join(self.tier_pars)}.")
        self.estim_start_time = pd.Timestamp.now()

        # TODO: Add option to only estimate for some tier samples not all that exist in the tier
        # Get list of tier samples or groups
        # If there is only one entity in the tier, then do not create a subfolder
        if len(self.tier_entities) == 1:
            folder_names = ['']
            list_of_tier_entity_lists = [self.tier_entities]
        # Check if the tier has groups
        elif len(self.tier_groups):
            folder_names = self.tier_groups
            list_of_tier_entity_lists = [self.data.get_entity_list_of_group(g_id) for g_id in self.tier_groups]
        else:
            folder_names = self.tier_entities
            list_of_tier_entity_lists = [[entity_id] for entity_id in self.tier_entities]

        for group_name, entity_list in zip(folder_names, list_of_tier_entity_lists):
            # Create estimation folder and set it in TierCodeGenerator and EstimationRunner objects
            output_folder = f"{self.output_folder}/{group_name}"
            os.makedirs(output_folder, exist_ok=True)
            self.tier_structure.estimation_runner.estim_files_dir = output_folder
            self.code_generator.output_folder = output_folder
            # Generate estimation files
            self.code_generator.generate_code(entity_list=entity_list, pseudo_data_weight=pseudo_data_weight)

            # Run estimation for name sample
            success = self.tier_structure.estimation_runner.run_estimation(hide_output=hide_output)
            if not success:
                print(f"Estimation for {self.name} tier with parameters {' '.join(self.tier_pars)} failed for tier "
                      f"entity or group {group_name}.")
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

        for tier_name in self.tier_structure.get_all_tiers_below(self.name):
            # Entity data
            tier = self.tier_structure.tiers[tier_name]
            for e_id in tier.data._entities:
                for dt in tier.data.entity_data_types:
                    varname = f'{dt}_{e_id}'
                    if varname in estimation_errors:
                        self.entity_data_errors.loc[(tier_name, e_id), dt] = estimation_errors[varname]
            # Group data
            for g_id in tier.data._groups:
                for dt in tier.data.group_data_types:
                    varname = f'{dt}_{g_id}'
                    if varname in estimation_errors:
                        self.group_data_errors.loc[(tier_name, g_id), dt] = estimation_errors[varname]

    def save_results(self):
        self.pars_df.to_csv(f"{self.output_folder}/{self.name}_pars.csv")
        self.entity_data_errors.to_csv(f"{self.output_folder}/{self.name}_entity_data_errors.csv")
        self.group_data_errors.to_csv(f"{self.output_folder}/{self.name}_group_data_errors.csv")

    def load_results(self):
        self.pars_df = pd.read_csv(f"{self.output_folder}/{self.name}_pars.csv", index_col='entity')
        self.entity_data_errors = pd.read_csv(f"{self.output_folder}/{self.name}_entity_data_errors.csv",
                                              index_col=['tier', 'entity'])
        self.group_data_errors = pd.read_csv(f"{self.output_folder}/{self.name}_group_data_errors.csv",
                                             index_col=['tier', 'group'])

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
            raise Exception(f"Missing template file for {missing_file}.")

    def check_all_files_exist(self, folder):
        files = [f"{tf}_{self.tier_estimator.tier_structure.species_name}.m" for tf in self.FILES_NEEDED]
        complete, missing_file = check_files_exist_in_folder(folder, files)
        return complete, missing_file

    def generate_mydata_file(self, entity_list, pseudo_data_weight=0.1):
        mydata_template = open(
            f'{self.tier_estimator.template_folder}/mydata_{self.tier_estimator.tier_structure.species_name}.m', 'r')
        mydata_out = open(f'{self.output_folder}/mydata_{self.tier_estimator.tier_structure.species_name}.m', 'w')

        entity_mydata_code_list = []
        group_mydata_code_list = []
        entity_data_types = set()
        group_data_types = set()
        tier_entities = {}
        tier_groups = {}
        tier_subtree = {entity_id: {} for entity_id in entity_list}
        groups_of_entity = {}
        for tier_name in self.tier_structure.get_all_tiers_below(self.tier_estimator.name):
            tier = self.tier_structure.tiers[tier_name]

            # Get list of entities and groups to include in the estimation
            tier_entities_to_include = []
            tier_group_list = []
            for entity_id in entity_list:
                te_list = self.tier_structure.entities_in_tier_below_from_entity_list(
                    tier_name=self.tier_estimator.name, tier_below=tier_name, entity_list=[entity_id]
                )
                tier_entities_to_include.extend(te_list)
                tier_group_list.extend(tier.data.get_group_list_from_entity_list(te_list))

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
            tier_entities[tier_name] = tier_entities_to_include
            tier_groups[tier_name] = tier_group_list
            groups_of_entity.update(tier.data.get_groups_of_entities(tier_entities_to_include))

        entity_data_code = '\n'.join(entity_mydata_code_list)
        group_data_code = '\n'.join(group_mydata_code_list)

        entity_data_types_code = generate_meta_data_code(var_name='entity_data_types',
                                                         formatted_data=format_list_of_strings_in_matlab(list(entity_data_types)))
        group_data_types_code = generate_meta_data_code(var_name='group_data_types',
                                                        formatted_data=format_list_of_strings_in_matlab(list(group_data_types)))
        entity_list_code = generate_tier_variable_code(
            var_name='entity_list',
            formatted_data=format_list_of_strings_in_matlab(entity_list),
            label='List of entities',
            pars_init_access=True,
        )

        # List of entity ids per tier included in the estimation
        tier_entities_code = generate_tier_variable_code(
            var_name='tier_entities',
            formatted_data=format_dict_in_matlab(
                {t: format_list_of_strings_in_matlab(g_list, double_brackets=True) for t, g_list in tier_entities.items()}
            ),
            label='List of entity ids for each tier',
        )

        # List of group ids per tier included in the estimation
        tier_groups_code = generate_tier_variable_code(
            var_name='tier_groups',
            formatted_data=format_dict_in_matlab(
                {t: format_list_of_strings_in_matlab(g_list, double_brackets=True) for t, g_list in tier_groups.items()}
            ),
            label='List of groups ids for each tier',
        )

        # Subtree of hierarchical structure
        data_to_format = {}
        for entity_id, subtree in tier_subtree.items():
            data_to_format[entity_id] = format_dict_in_matlab(
                {t: format_list_of_strings_in_matlab(e_list, double_brackets=True) for t, e_list in subtree.items()})
        tier_subtree_code = generate_tier_variable_code(
            var_name='tier_subtree',
            formatted_data=format_dict_in_matlab(data_to_format),
            label='Tier subtree',
        )

        # Groups of entity
        groups_of_entity_code = generate_tier_variable_code(
            var_name='groups_of_entity',
            formatted_data=format_dict_in_matlab(
                {e_id: format_list_of_strings_in_matlab(g_list, double_brackets=True) for e_id, g_list in
                 groups_of_entity.items()}
            ),
            label='Groups each entity belongs to'
        )

        # Tier parameters
        tier_pars_code = generate_tier_variable_code(
            var_name='tier_pars',
            formatted_data=format_list_of_strings_in_matlab(self.tier_estimator.tier_pars),
            label='Tier parameters',
            comment='Tier parameters',
            pars_init_access=True)

        # Initial values for tier parameters
        tier_par_init_values = self.tier_estimator.tier_structure.get_init_par_values(
            tier_name=self.tier_estimator.name, entity_list=entity_list).to_dict()
        tier_par_init_values_code = generate_meta_data_code(
            var_name='tier_par_init_values',
            formatted_data=format_dict_in_matlab(
                {p: format_dict_in_matlab(init_values) for p, init_values in tier_par_init_values.items()})
        )

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
        mydata_out.close()
        mydata_template.close()

    def generate_pars_init_file(self, entity_list):
        # TODO: Use multitier.ind_list_from_tier_sample_list()
        if entity_list == 'all':
            entity_list = self.tier_estimator.tier_structure.get_all_entities_in_tier(self.tier_estimator.name)
        pars_dict = self.tier_estimator.tier_structure.get_full_pars_dict(self.tier_estimator.name, entity_list[0])
        pars_init_template = open(
            f'{self.tier_estimator.template_folder}/pars_init_{self.tier_estimator.tier_structure.species_name}.m',
            'r')
        pars_init_out = open(f'{self.output_folder}/pars_init_{self.tier_estimator.tier_structure.species_name}.m', 'w')

        src = Template(pars_init_template.read())
        result = src.substitute(**pars_dict)

        print(result, file=pars_init_out)
        pars_init_out.close()
        pars_init_template.close()

    def generate_predict_file(self):
        shutil.copy(
            src=f"{self.tier_estimator.template_folder}/predict_{self.tier_estimator.tier_structure.species_name}.m",
            dst=f"{self.output_folder}")

    def generate_run_file(self):
        run_template = open(
            f'{self.tier_estimator.template_folder}/run_{self.tier_estimator.tier_structure.species_name}.m', 'r')
        run_out = open(f'{self.output_folder}/run_{self.tier_estimator.tier_structure.species_name}.m', 'w')
        src = Template(run_template.read())
        result = src.substitute(self.tier_estimator.estimation_settings)
        print(result, file=run_out)
        run_out.close()
        run_template.close()

    def generate_code(self, entity_list, pseudo_data_weight=0.1):
        self.generate_mydata_file(entity_list=entity_list, pseudo_data_weight=pseudo_data_weight)
        self.generate_pars_init_file(entity_list=entity_list)
        self.generate_predict_file()
        self.generate_run_file()
