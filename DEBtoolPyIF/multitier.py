import pandas as pd
from string import Template
import os
import shutil
from tabulate import tabulate

from .data_sources import DataCollection
from .matlab_wrapper import EstimationRunner
from .utils import check_files_exist_in_folder, format_list_data, format_dict_data, format_aux_data


class MultiTierStructure:
    def __init__(self, species_name: str, ind_tiers: pd.DataFrame, data: DataCollection, pars: dict,
                 tier_pars: dict, template_folders: dict, output_folder: str, estimation_settings: dict,
                 tier_output_folders: dict):
        self.data = data
        self.species_name = species_name
        self.ind_tiers = ind_tiers
        self.tier_names = list(self.ind_tiers.columns)
        self.output_folder = output_folder
        self.pars = pars
        self.tier_pars = tier_pars
        self.tiers = {tier: None for tier in self.tier_names}
        self.build_tiers(estimation_settings=estimation_settings, template_folders=template_folders,
                         tier_output_folders=tier_output_folders)
        self.estimation_runner = EstimationRunner(species_name=self.species_name)

    def build_tiers(self, estimation_settings, template_folders, tier_output_folders):

        # Create estimators for each name
        for tier_name in self.tier_names:
            if tier_name not in template_folders:
                raise Exception(f"Template folder for name {tier_name} is not defined.")
            tier_pars_str = ' '.join(self.tier_pars[tier_name])
            if not all([p in self.pars for p in self.tier_pars[tier_name]]):
                raise Exception(f"Cannot estimate name pars {tier_pars_str} for {tier_name} name as they"
                                f" are not all estimated in the previous name.")
            # Create output folder for name estimation
            if tier_name not in tier_output_folders:
                tier_output_folder = f"{self.output_folder}/{tier_name}/{tier_pars_str}"
            else:
                tier_output_folder = f"{self.output_folder}/{tier_name}/{tier_output_folders[tier_name]}"

            os.makedirs(tier_output_folder, exist_ok=True)
            self.tiers[tier_name] = TierEstimator(tier_structure=self,
                                                  tier_name=tier_name,
                                                  tier_pars=self.tier_pars[tier_name],
                                                  template_folder=template_folders[tier_name],
                                                  output_folder=tier_output_folder,
                                                  estimation_settings=estimation_settings[tier_name])

    def get_tier_sample_inds(self, tier_name, tier_sample_list='all'):
        inds_in_tier = self.ind_tiers[tier_name]
        if tier_sample_list == 'all':
            tier_sample_list = inds_in_tier.unique()
        return {ts_id: list(ids.index) for ts_id, ids in inds_in_tier.groupby(inds_in_tier) if
                ts_id in tier_sample_list}

    def ind_list_from_tier_sample_list(self, tier_name, tier_sample_list='all'):
        inds_in_tier = self.ind_tiers[tier_name]
        if tier_sample_list == 'all':
            return list(inds_in_tier.index)
        return list(inds_in_tier[inds_in_tier.isin(tier_sample_list)].index)

    def get_prev_tier(self, tier_name):
        if tier_name == self.tier_names[0]:
            return None
        return self.tier_names[self.tier_names.index(tier_name) - 1]

    def get_pars_from_prev_tier(self, tier_name):
        return self.tiers[self.get_prev_tier(tier_name)].pars_df

    def get_init_par_values(self, tier_name, tier_sample_list='all'):
        if tier_sample_list == 'all':
            tier_sample_list = self.ind_tiers[tier_name].unique()
        init_par_values = pd.DataFrame(columns=self.tier_pars[tier_name], index=tier_sample_list)

        prev_tier = self.get_prev_tier(tier_name)
        # Case for top tier
        if prev_tier is None:
            for ts_id in tier_sample_list:
                for par in self.tier_pars[tier_name]:
                    init_par_values.loc[ts_id, par] = self.pars[par]
        else:
            prev_tier_par_values = self.get_pars_from_prev_tier(tier_name)
            for ts_id in tier_sample_list:
                prev_ts_id = self.ind_tiers.groupby(tier_name).get_group(ts_id)[prev_tier].iloc[0]
                for par in self.tier_pars[tier_name]:
                    # Use pseudo data if available
                    if par in self.tiers[tier_name].pseudo_data:
                        init_par_values.loc[ts_id, par] = self.tiers[tier_name].pseudo_data.loc[ts_id, par]
                    # Else use previous tier value
                    else:
                        init_par_values.loc[ts_id, par] = prev_tier_par_values.loc[prev_ts_id, par]

        return init_par_values

    def get_full_pars_dict(self, tier_name, tier_sample):
        pars_dict = self.pars.copy()
        ts_tiers = self.ind_tiers.groupby(tier_name).get_group(tier_sample).iloc[0]
        for t in self.tier_names:
            if t == tier_name:
                break
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
        self.tier_sample_list = self.tier_structure.ind_tiers[tier_name].unique()
        self.template_folder = template_folder
        self.output_folder = output_folder
        self.estimation_settings = estimation_settings
        self.pseudo_data = extra_pseudo_data
        self.extra_info = extra_info

        self.set_tier_parameters(tier_pars)

        self.ind_data_errors = pd.DataFrame(columns=['tier_sample'] + self.tier_structure.data.ind_data_types,
                                            index=self.tier_structure.data.individuals)
        self.ind_data_errors.index.name = 'ind_id'
        self.ind_data_errors['tier_sample'] = self.tier_structure.ind_tiers[tier_name]

        self.group_data_errors = pd.DataFrame(columns=['tier_sample'] + self.tier_structure.data.group_data_types,
                                              index=self.tier_structure.data.groups)
        self.group_data_errors['tier_sample'] = ''
        self.group_data_errors.index.name = 'group_id'
        for g_id in self.group_data_errors.index:
            inds_in_group = self.tier_structure.data.inds_in_group[g_id]
            # Assume all individuals in the group have the same tier sample
            self.group_data_errors.loc[g_id, 'tier_sample'] = self.tier_structure.ind_tiers[tier_name].loc[
                inds_in_group[0]]

        self.tier_errors = pd.DataFrame(
            columns=self.tier_structure.data.ind_data_types + self.tier_structure.data.group_data_types,
            index=self.tier_sample_list)
        self.tier_errors.index.name = 'tier_sample'

        self.code_generator = TierCodeGenerator(tier=self)

    @property
    def estimation_complete(self):
        return self.pars_df.notna().all().all()

    def set_tier_parameters(self, tier_pars):
        self.tier_pars = tier_pars
        self.pars_df = pd.DataFrame(columns=self.tier_pars,
                                    index=self.tier_structure.ind_tiers[self.name].unique())
        self.pars_df.index.name = 'tier_sample'

    def estimate(self, pseudo_data_weight=0.1, save_results=True, print_results=True, hide_output=True):
        # TODO: Add options of estimation runner
        print(f"Running estimation for {self.name} tier with parameters {' '.join(self.tier_pars)}.")

        # Create files of estimation
        self.code_generator.generate_predict_file()
        self.code_generator.generate_run_file()

        # Check if this is an individual name
        if len(self.tier_sample_list) == len(self.tier_structure.ind_tiers.index.values):
            list_of_tier_sample_lists = [v for v in self.tier_structure.data.inds_in_group.values()]
        else:
            list_of_tier_sample_lists = [[ts_id] for ts_id in self.tier_sample_list]

        for ts_list in list_of_tier_sample_lists:
            self.code_generator.generate_mydata_file(tier_sample_list=ts_list, pseudo_data_weight=pseudo_data_weight)
            self.code_generator.generate_pars_init_file(tier_sample_list=ts_list)

            # Run estimation for name sample
            success = self.tier_structure.estimation_runner.run_estimation(
                run_files_dir=self.output_folder,
                hide_output=hide_output)
            if not success:
                print(f"Estimation for {self.name} tier with parameters {' '.join(self.tier_pars)} failed.")
                continue

            self.fetch_pars(tier_sample_list=ts_list)

            self.fetch_errors(tier_sample_list=ts_list)

        if print_results:
            self.print_results(tier_sample_list=self.tier_sample_list)
        if save_results:
            self.save_results()

    def fetch_pars(self, tier_sample_list):
        pars = self.tier_structure.estimation_runner.fetch_pars_from_mat_file(
            run_files_dir=self.output_folder,
        )
        # Store parameter values
        if len(self.pars_df) == 1:
            self.pars_df.iloc[0] = pars
        else:
            for par in self.tier_pars:
                for ts_id in tier_sample_list:
                    self.pars_df.loc[ts_id, par] = pars[f'{par}_{ts_id}']

    def fetch_errors(self, tier_sample_list):
        estimation_errors = self.tier_structure.estimation_runner.fetch_errors_from_mat_file(
            run_files_dir=self.output_folder
        )
        # Store individual data errors
        ind_list = self.tier_structure.ind_list_from_tier_sample_list(self.name, tier_sample_list)

        for dt in self.tier_structure.data.ind_data_types:
            for ind_id in ind_list:
                varname = f'{dt}_{ind_id}'
                if varname in estimation_errors:
                    self.ind_data_errors.loc[ind_id, dt] = estimation_errors[varname]
            self.tier_errors.loc[tier_sample_list, dt] = self.ind_data_errors.loc[ind_list, dt].mean()
        # Store group data errors
        group_list = self.tier_structure.data.get_group_list_from_ind_list(ind_list=ind_list)
        for dt in self.tier_structure.data.group_data_types:
            for group_id in group_list:
                varname = f'{dt}_{group_id}'
                if varname in estimation_errors:
                    self.group_data_errors.loc[group_id, dt] = estimation_errors[varname]
            self.tier_errors.loc[tier_sample_list, dt] = self.group_data_errors.loc[group_list, dt].mean()

    def save_results(self):
        self.pars_df.to_csv(f"{self.output_folder}/{self.name}_pars.csv")
        self.ind_data_errors.to_csv(f"{self.output_folder}/{self.name}_ind_data_errors.csv")
        self.group_data_errors.to_csv(f"{self.output_folder}/{self.name}_group_data_errors.csv")
        self.tier_errors.to_csv(f"{self.output_folder}/{self.name}_tier_errors.csv")

    def load_results(self):
        self.pars_df = pd.read_csv(f"{self.output_folder}/{self.name}_pars.csv", index_col='tier_sample')
        self.ind_data_errors = pd.read_csv(f"{self.output_folder}/{self.name}_ind_data_errors.csv",
                                           index_col='ind_id')
        self.group_data_errors = pd.read_csv(f"{self.output_folder}/{self.name}_group_data_errors.csv",
                                             index_col='group_id')
        self.tier_errors = pd.read_csv(f"{self.output_folder}/{self.name}_tier_errors.csv",
                                       index_col='tier_sample')

    def print_results(self, tier_sample_list):
        print(tabulate(self.tier_errors.loc[tier_sample_list, :], tablefmt="simple", showindex=True, headers="keys"))
        print('\n')

    def print_pars(self, tier_sample_list):
        print(tabulate(self.pars_df.loc[tier_sample_list, :], tablefmt="simple", showindex=True, headers="keys"))


class TierCodeGenerator:
    FILES_NEEDED = ['mydata', 'pars_init', 'predict', 'run']

    def __init__(self, tier: TierEstimator):
        self.tier = tier

        complete, missing_file = self.check_all_files_exist(self.template_folder)
        if not complete:
            raise Exception(f"Missing template file for {missing_file}.")

    @property
    def name(self):
        return self.tier.name

    @property
    def tier_structure(self):
        return self.tier.tier_structure

    @property
    def output_folder(self):
        return self.tier.output_folder

    @property
    def template_folder(self):
        return self.tier.template_folder

    @property
    def estimation_settings(self):
        return self.tier.estimation_settings

    @property
    def species_name(self):
        return self.tier_structure.species_name

    @property
    def tier_pars(self):
        return self.tier.tier_pars

    @property
    def data(self):
        return self.tier_structure.data

    def check_all_files_exist(self, folder):
        files = [f"{tf}_{self.species_name}.m" for tf in self.FILES_NEEDED]
        complete, missing_file = check_files_exist_in_folder(folder, files)
        return complete, missing_file

    def generate_mydata_file(self, tier_sample_list, pseudo_data_weight=0.1):
        mydata_template = open(f'{self.template_folder}/mydata_{self.species_name}.m', 'r')
        mydata_out = open(f'{self.output_folder}/mydata_{self.species_name}.m', 'w')

        tier_sample_inds = self.tier_structure.get_tier_sample_inds(self.name, tier_sample_list)
        ind_list = self.tier_structure.ind_list_from_tier_sample_list(self.name, tier_sample_list)
        group_list = self.data.get_group_list_from_ind_list(ind_list=ind_list)

        ind_data_code = '\n'.join(self.data.get_ind_data_code(ind_list=ind_list))
        group_data_code = '\n'.join(self.data.get_group_data_code(ind_list=ind_list))
        group_list_code = format_aux_data(
            var_name='group_list',
            formatted_data=format_list_data(group_list, brackets=True),
            label='List of individuals', comment='List of individuals',
        )
        ind_list_code = format_aux_data(
            var_name='ind_list',
            formatted_data=format_list_data(ind_list, brackets=True),
            label='List of individuals', comment='List of individuals',
            pars_init_access=True)
        ind_data_types = self.data.ind_data_types.__repr__()[1:-1]
        group_data_types = self.data.group_data_types.__repr__()[1:-1]
        groups_of_ind = self.data.get_groups_of_ind_list(ind_list)
        groups_of_ind_code = format_aux_data(
            var_name='groups_of_ind',
            formatted_data=format_dict_data({ind_id: '{' + format_list_data(g_list, brackets=True) + '}'
                                             for ind_id, g_list in groups_of_ind.items()}),
            label='Groups of individuals',
            comment='Groups of individuals',
        )
        tier_sample_list_code = format_aux_data(
            var_name='tier_sample_list',
            formatted_data=format_list_data(list(tier_sample_inds.keys()), brackets=True),
            label='Tier sample list',
            comment='Tier sample list',
            pars_init_access=True)
        tier_sample_inds_code = format_aux_data(
            var_name='tier_sample_inds',
            formatted_data=format_dict_data({ts_id: '{' + format_list_data(ids, brackets=True) + '}'
                                             for ts_id, ids in tier_sample_inds.items()}),
            label='List of individuals that belong to the name sample',
            comment='List of individuals that belong to the name sample',
        )
        tier_pars_code = format_aux_data(
            var_name='tier_pars',
            formatted_data=format_list_data(self.tier_pars, brackets=True),
            label='Tier parameters',
            comment='Tier parameters',
            pars_init_access=True)
        tier_par_init_values = self.tier_structure.get_init_par_values(self.name, tier_sample_list).to_dict()
        tier_par_init_values_code = format_dict_data(
            {p: format_dict_data(init_values) for p, init_values in tier_par_init_values.items()})

        src = Template(mydata_template.read())
        result = src.substitute(
            group_data=group_data_code,
            group_data_types=group_data_types,
            group_list=group_list_code,
            individual_data=ind_data_code,
            ind_data_types=ind_data_types,
            ind_list=ind_list_code,
            groups_of_ind=groups_of_ind_code,
            tier_sample_list=tier_sample_list_code,
            tier_sample_inds=tier_sample_inds_code,
            tier_pars=tier_pars_code,
            tier_par_init_values=tier_par_init_values_code,
            extra_info=self.tier.extra_info,
            pseudo_data_weight=pseudo_data_weight
        )
        print(result, file=mydata_out)
        mydata_out.close()
        mydata_template.close()

    def generate_pars_init_file(self, tier_sample_list):
        if tier_sample_list == 'all':
            tier_sample_list = self.tier_structure.ind_tiers[self.name].unique()
        pars_dict = self.tier_structure.get_full_pars_dict(self.name, tier_sample_list[0])
        pars_init_template = open(f'{self.template_folder}/pars_init_{self.species_name}.m', 'r')
        pars_init_out = open(f'{self.output_folder}/pars_init_{self.species_name}.m', 'w')

        src = Template(pars_init_template.read())
        result = src.substitute(**pars_dict)

        print(result, file=pars_init_out)
        pars_init_out.close()
        pars_init_template.close()

    def generate_predict_file(self):
        shutil.copy(src=f"{self.template_folder}/predict_{self.species_name}.m", dst=f"{self.output_folder}")

    def generate_run_file(self):
        run_template = open(f'{self.template_folder}/run_{self.species_name}.m', 'r')
        run_out = open(f'{self.output_folder}/run_{self.species_name}.m', 'w')
        src = Template(run_template.read())
        result = src.substitute(self.estimation_settings)
        print(result, file=run_out)
        run_out.close()
        run_template.close()

    def generate_code(self, tier_sample_list, pseudo_data_weight=0.1):
        self.generate_mydata_file(tier_sample_list=tier_sample_list, pseudo_data_weight=pseudo_data_weight)
        self.generate_pars_init_file(tier_sample_list=tier_sample_list)
        self.generate_predict_file()
        self.generate_run_file()


def estimate_all_par_combinations(tier_structure: MultiTierStructure, pars_combinations: list,
                                  reestimate_complete=False):
    if isinstance(reestimate_complete, bool):
        reestimate_complete = {tier_name: reestimate_complete for tier_name in tier_structure.tier_names}

    prev_par_comb = {tier: None for tier in tier_structure.tier_names}
    pars_combinations.sort()
    for par_comb in pars_combinations:
        for i, tier in enumerate(tier_structure.tiers.values()):
            tier_pars = par_comb[i]
            #  Skip tier estimation if the tier pars of the previous combination are the same
            if tier_pars == prev_par_comb[tier.name]:
                continue
            if tier.tier_pars != tier_pars:
                tier_structure.set_tier_parameters(tier.name, tier_pars)
                tier.output_folder = f"{tier_structure.output_folder}/{tier.name}/{' '.join(tier_pars)}"
                os.makedirs(tier.output_folder, exist_ok=True)

            # Check if files exist
            all_estim_files, _ = tier.code_generator.check_all_files_exist(folder=tier.template_folder)
            all_results_files, _ = check_files_exist_in_folder(folder_name=tier.output_folder,
                                                               files=[f"{tier.name}_{ft}.csv" for ft in
                                                                      TierEstimator.OUTPUT_FILES])
            if all_estim_files and all_results_files:
                tier.load_results()
                prev_par_comb[tier.name] = tier_pars
                if tier.estimation_complete and not reestimate_complete[tier.name]:
                    continue
            tier.estimate()

    return tier_structure
