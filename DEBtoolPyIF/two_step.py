from datetime import datetime as dt
import os
import pandas as pd
import numpy as np

from .code_generator import GroupStepCodeGenerator, IndividualStepCodeGenerator
from .data_sources import DataCollection
from .matlab_wrapper import EstimationRunner


class TwoStepEstimator:
    def __init__(self, pars: list, species_name: str, group_step_template_folder: str,
                 ind_step_template_folder: str, main_output_folder: str, data: DataCollection):

        self.pars = pars
        self.species_name = species_name
        self.group_step_template_folder = group_step_template_folder
        self.ind_step_template_folder = ind_step_template_folder
        self.main_output_folder = main_output_folder

        # Code generators
        self.data = data
        self.group_step_code_generator = GroupStepCodeGenerator(group_step_template_folder, [], species_name, data)
        self.ind_step_code_generator = IndividualStepCodeGenerator(ind_step_template_folder, [], species_name, data)

        # MATLAB wrapper to run estimations
        # TODO: Option to not start MATLAB
        print('Starting MATLAB...')
        self.runner = EstimationRunner()

    def group_step_estimation(self, estimation_settings: dict, output_folder=None, ind_list=None, ind_data_weight=None,
                              save_pars=True, extra_info=None, **wrapper_settings):
        # Create files of estimation
        if output_folder is None:
            output_folder = f"{self.main_output_folder}/Group Step"
        self.group_step_code_generator.set_estimation_settings(**estimation_settings)
        self.group_step_code_generator.generate_code(output_folder=output_folder, ind_list=ind_list,
                                                     ind_data_weight=ind_data_weight, extra_info=extra_info)

        # Run estimation
        print('Running group step...')
        results = self.runner.run_estimation(run_files_dir=output_folder, species_name=self.species_name,
                                             **wrapper_settings)
        group_pars = self.get_group_pars_from_all_pars(results['pars'])
        if save_pars:
            with open(f'{output_folder}/group_pars.txt', 'w') as group_pars_file:
                for p, v in group_pars.items():
                    print(p, v, file=group_pars_file)

        return group_pars

    def get_group_pars_from_all_pars(self, all_pars):
        return {p: all_pars[p] for p in self.pars}

    def ind_step_estimation(self, default_pars: dict, ind_pars: list, estimation_settings: dict, output_folder=None,
                            ind_groups_list=None, use_pseudo_data=True, pseudo_data_weight=0.1,
                            species_data_types=None, species_data_weight="1 / numel(metaData.data_0)",
                            extra_info=None, extra_par_values='', **wrapper_settings):
        # Check both ind_pars and default_pars are properly defined
        if species_data_types is None:
            species_data_types = []
        if not len(ind_pars):
            raise Exception("Individual parameters were not set in ind_pars.")

        self.ind_step_code_generator.individual_params = ind_pars

        # Create files for estimation
        if output_folder is None:
            output_folder = f"{self.main_output_folder}/{' '.join(ind_pars)}"
        if use_pseudo_data:
            pseudo_data = {}
            # Find pseudo-data value for parameters that are ind_pars, including default parameters that have a suffix
            for p, v in default_pars.items():
                if any([i in p for i in ind_pars]):
                    pseudo_data[p] = v
        else:
            pseudo_data = None
        self.ind_step_code_generator.set_estimation_settings(**estimation_settings)
        my_data_options = dict(pseudo_data=pseudo_data, species_data_weight=species_data_weight, ind_data_weight=1,
                               pseudo_data_weight=pseudo_data_weight)
        self.ind_step_code_generator.generate_code(output_folder=output_folder, default_pars=default_pars, ind_list=[],
                                                   extra_info=extra_info, extra_par_values=extra_par_values,
                                                   **my_data_options)

        # Create files to save parameters and errors
        ind_pars_file = open(f"{output_folder}/ind_pars.csv", 'w')
        print(f"id,{','.join(ind_pars)}", file=ind_pars_file)
        errors_file = open(f"{output_folder}/errors.csv", 'w')

        print(f"id,loss,{','.join(species_data_types + self.data.group_data_types + self.data.ind_data_types)}",
              file=errors_file)

        # Print header
        print('\n\n' + dt.today().isoformat(sep=' ', timespec='seconds'))
        max_len_id = max([len(str(ind)) for ind in self.data.individuals])
        header = 'id' + ' ' * (max_len_id - 2) + " | " + ' '.join(
            ['loss   '] + [str(gd).ljust(7) for gd in species_data_types] +
            [str(ds).ljust(7) for ds in self.data.group_data_types] +
            [str(ds).ljust(7) for ds in self.data.ind_data_types]) + \
                 ' | ' + ' '.join([p.ljust(10) for p in ind_pars])
        print(header)

        # Estimate for each individual
        if ind_groups_list is None:
            ind_groups_list = self.data.inds_in_group
        for group_id, ind_list in ind_groups_list.items():
            # Create my_data.m file
            self.ind_step_code_generator.create_mydata_file(output_folder=output_folder, ind_list=ind_list,
                                                            group_list=[group_id], extra_info=extra_info,
                                                            **my_data_options)

            # Run estimation
            results = self.runner.run_estimation(run_files_dir=output_folder, species_name=self.species_name,
                                                 **wrapper_settings)
            if not results['success']:
                print('BUG!!! BIG BUG!!!')

            group_data_errors = [f"{results['estimation_errors']['final']['sb_1']:.5f}"]
            for ds in self.data.group_data_sources:
                if group_id in ds.groups:
                    group_data_errors.append(f"{results['estimation_errors']['re'][f'{ds.TYPE}_{group_id}']:.5f}")
            # TODO: Save group_id in estimation
            for i, ind in enumerate(ind_list):
                # Get parameter values for the individual
                ind_par_values = []
                for p in ind_pars:
                    ind_par_values.append(results['pars'][f'{p}_{ind}'])
                print(f"{ind},{','.join([f'{p:.8f}' for p in ind_par_values])}", file=ind_pars_file)

                # Get errors measures for the individual
                ind_data_errors = []
                for data_type in self.data.ind_data_types:
                    if f'{data_type}_{ind}' in results['estimation_errors']['re']:
                        ind_data_errors.append(f"{results['estimation_errors']['re'][f'{data_type}_{ind}']:.5f}")
                    else:
                        ind_data_errors.append("-------")

                print(f"{ind},{','.join(group_data_errors)},{','.join(ind_data_errors)}", file=errors_file)

                # Print errors and individual parameter values
                if i == 0:
                    group_print_str = ' '.join(group_data_errors)
                else:
                    group_print_str = ' ' * len(group_print_str)
                ind_info = f"{ind}".ljust(max_len_id) + " | " + group_print_str + " " \
                           + ' '.join(ind_data_errors) + \
                           ' | ' + ' '.join([f"{p:.4e}" for p in ind_par_values])
                print(ind_info)

        ind_pars_file.close()

        # Create my_data.m file with all inds
        self.ind_step_code_generator.create_mydata_file(output_folder=output_folder,
                                                        group_list=list(ind_groups_list.keys()),
                                                        ind_list=[ind_id for ind_list in ind_groups_list.values() for
                                                                  ind_id in ind_list],
                                                        extra_info=extra_info,
                                                        **my_data_options)
        # Save all individual pars in the results.mat file
        self.runner.eng.initialize_ind_pars_from_csv('ind_pars.csv', self.species_name, nargout=0)


# TODO: Make compatible with breed data
def compile_results(estimator: TwoStepEstimator, pars_to_get_stats, ind_step_estimations_folder=None):
    print(f"Compiling results for estimations with parameters", *pars_to_get_stats, "...", end=' ', sep=' ')
    if ind_step_estimations_folder is None:
        ind_step_estimations_folder = estimator.main_output_folder
    stats_folder = f"{estimator.main_output_folder}/Stats"
    if not os.path.exists(stats_folder):
        os.makedirs(stats_folder)
    # Create files to save statistics on parameters
    par_files = {p: open(f"{stats_folder}/{p}_dist.csv", 'w') for p in pars_to_get_stats}
    for p, f in par_files.items():
        print(f"ind_pars,n_ind_pars,mean,std,mad,cv,qcd,skew,kurt", file=f)
    # Create error file
    error_summary = open(f"{stats_folder}/error_summary.csv", 'w')
    header = f"ind_pars,n_ind_pars,loss,{','.join([f'{ds}_min,{ds}_avg,{ds}_max' for ds in estimator.data.data_types])}"
    print(header, file=error_summary)

    # Iterate through estimation folders
    for estim in os.listdir(ind_step_estimations_folder):
        estim_folder = f"{ind_step_estimations_folder}/{estim}"
        if estim == 'Group Step' or estim == 'Analysis' or not os.path.isdir(estim_folder):
            continue
        ind_pars = estim.split()
        n_ind_pars = len(ind_pars)

        # Skip estimations that contain a parameter not in pars_to_get_stats
        if any([p not in pars_to_get_stats for p in ind_pars]):
            continue

        # Compute error stats
        error_df = pd.read_csv(f"{estim_folder}/errors.csv", index_col='id', na_values='-------')
        group_size = max(
            [len(ind_list) for ind_list in
             estimator.data.inds_in_group.values()])  # Assumes all groups have the same size
        line = f"{estim} ,{n_ind_pars},{error_df['loss'].sum() / group_size:.5f}"
        for ds in estimator.data.data_types:
            line += f",{error_df[ds].min():.5f},{error_df[ds].mean():.5f},{error_df[ds].max():.5f}"
        print(line, file=error_summary)

        # Compute parameter statistics
        pars_df = pd.read_csv(f"{estim_folder}/ind_pars.csv", index_col='id')
        for p in ind_pars:
            par_vals = pars_df[p]
            mean = par_vals.mean()
            std = par_vals.std()
            mad = np.median(np.abs(par_vals - par_vals.median()))
            cv = std / mean
            q1 = par_vals.quantile(0.25)
            q3 = par_vals.quantile(0.75)
            qcd = (q3 - q1) / (q1 + q3)
            skew = par_vals.skew()
            kurt = par_vals.kurt()
            print(f"{estim} ,{n_ind_pars},{mean:.6f},{std:.6f},{mad:.6f},{cv:.6f},{qcd:.6f},{skew:.6f},{kurt:.6f}",
                  file=par_files[p])

    error_summary.close()
    for f in par_files.values():
        f.close()
    print('Done!')
