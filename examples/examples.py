from DEBtoolPyIF.code_generator import TrainingCodeGenerator, TestingCodeGenerator
# from matlab_wrapper import run_estimation, EstimationRunner
from DEBtoolPyIF.data_sources import *
# from cross_validation import HoldoutCV
from itertools import combinations, product
# from monte_carlo import MonteCarloEstimation
from DEBtoolPyIF.two_step import TwoStepEstimator, compile_results

import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import shutil


def run_simultaneous_estimations():
    params = ['p_Am', 'p_M', 'kap_X']
    species_name = 'Bos_taurus_Mertolenga'
    template_folder = "../Mertolenga/Training Template"
    # Data sources
    twds = TimeWeightDataSource(f"../../Data/ACBM/CSV Files/weights_clean.csv", id_col='sia', weight_col='weight',
                                age_col='age', bibkey=f'ACBM',
                                comment=f'Data from Mertolenga performance test')
    tfds = TimeCumulativeFeedDataSource(f"../../Data/ACBM/CSV Files/feed_consumption_clean.csv", id_col='sia',
                                        feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                        bibkey=f'ACBM',
                                        comment=f'Data from Mertolenga performance test')
    # wfds = WeightFeedDataSource(f"../../Data/ACBM/CSV Files/weight_intake_clean.csv", id_col='sia',
    #                             feed_col='cumul_dry', weight_col='weight',
    #                             bibkey=f"ACBM", comment=f'Data from Mertolenga performance test')
    runner = EstimationRunner()
    results = {}
    for nip in (2, 1, 3):
        for p_list in combinations(params, nip):
            # if p_list == ('p_Am','p_M'):
            #     continue
            print(p_list)
            gen = TrainingCodeGenerator(template_folder=template_folder, individual_params=p_list,
                                        species_name=species_name)
            gen.add_data_source(twds)
            gen.add_data_source(tfds)
            # gen.add_data_source(wfds)
            gen.set_estimation_settings(n_runs=1000, results_output_mode=3, pars_init_method=2, n_steps=1000)
            output_folder = f"../Mertolenga/Simultaneous/{' '.join(p_list)}"
            gen.generate_code(output_folder=output_folder)

            results[' '.join(p_list)] = runner.run_estimation(output_folder, species_name, window=False,
                                                              clear_before=True, hide_output=False)


def training_and_testing_code_generation():
    individual_params = [
        # 'p_Am',
        # 'p_M',
        # 'kap_X'
    ]
    species_name = 'Bos_taurus_Mertolenga'

    template_folder = "C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/" \
                      "DEB Parameter Estimation/Mertolenga/Training Template"
    output_folder = f"C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/" \
                    f"DEB Parameter Estimation/Mertolenga/Basic {' '.join(individual_params)}"
    # output_folder = "C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/" \
    #                 "DEB Parameter Estimation/Mertolenga/Mertolenga None"

    gen = TrainingCodeGenerator(template_folder=template_folder, individual_params=individual_params,
                                species_name=species_name)
    #
    # individual_params = ('p_Am', 'kap_X')
    # species_name = 'Bos_taurus_Mertolenga'
    #
    # template_folder = "C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/" \
    #                   "DEB Parameter Estimation/Mertolenga/Testing Template"
    # output_folder = f"C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/" \
    #                 f"DEB Parameter Estimation/Mertolenga/test"
    # pars = {'p_Am': 1758, 'kap_X': 0.1881, 'v': 0.2445, 'kap': 0.9532, 'p_M': 23.52, 'E_G': 8881, 'E_Hb': 6.008e+06,
    #         'E_Hx': 4.441e+07, 'E_Hp': 1.462e+08, 't_0': 230.6}
    # gen = TestingCodeGenerator(template_folder=template_folder, individual_params=individual_params,
    #                            species_name=species_name, default_pars=pars)

    # Add data
    twds = TimeWeightDataSource(f"../ACBM/CSV Files/weights_clean.csv", id_col='sia', weight_col='weight',
                                age_col='age', bibkey=f'Mertolenga',
                                comment=f'Data from Mertolenga performance test')
    gen.add_data_source(twds)
    tfds = TimeCumulativeFeedDataSource(f"../ACBM/CSV Files/feed_consumption_clean.csv", id_col='sia',
                                        feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                        bibkey=f'Mertolenga',
                                        comment=f'Data from Mertolenga performance test')
    gen.add_data_source(tfds)

    # Generate code
    gen.set_estimation_settings(n_runs=50, results_output_mode=3)
    gen.generate_code(output_folder=output_folder)

    # Run estimation with MATLAB
    pars, estimation_errors, meta_data = run_estimation(f"{output_folder}", species_name=species_name, window=False)


def holdout_cross_validation():
    individual_pars = [
        # 'p_Am',
        'p_M',
        # 'kap_X'
    ]
    if not len(individual_pars):
        individual_pars = ['None']
    group_pars = {'p_Am': 1800, 'kap_X': 0.3, 'v': 0.05, 'kap': 0.95, 'p_M': 25, 'E_G': 8000, 'E_Hb': 5e6, 'E_Hx': 1e7,
                  'E_Hp': 5e7, 't_0': 150}
    # for p in individual_pars:
    #     del group_pars[p]
    species_name = 'Bos_taurus_Mertolenga'
    data_folder = "C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/Data/ACBM/CSV Files"

    template_folder = "C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/" \
                      "DEB Parameter Estimation/Mertolenga/Testing Template"
    hcv = HoldoutCV(template_folder, individual_pars, group_pars, species_name)

    # Add data sources
    twds = TimeWeightDataSource(f"{data_folder}/weights_clean.csv", id_col='sia', weight_col='weight',
                                age_col='age', bibkey=f'Mertolenga',
                                comment=f'Data from Mertolenga performance test')
    hcv.add_data_source(twds)
    tfds = TimeCumulativeFeedDataSource(f"{data_folder}/feed_consumption_clean.csv", id_col='sia',
                                        feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                        bibkey=f'Mertolenga',
                                        comment=f'Data from Mertolenga performance test')
    hcv.add_data_source(tfds)

    # output_folder = "C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/" \
    #                 "DEB Parameter Estimation/Mertolenga/Holdout/holdout test"
    output_folder = f"C:/Users/diogo/OneDrive - Universidade de Lisboa/Terraprima/Code/" \
                    f"DEB Parameter Estimation/Mertolenga/Holdout/{' '.join(individual_pars)}"
    train_run_settings = dict(n_runs=50, results_output_mode=3, n_steps=500)
    test_run_settings = dict(n_runs=30, results_output_mode=3, n_steps=500)

    hcv.fit_predict(train_run_settings=train_run_settings, test_run_settings=test_run_settings, test_size=0.25,
                    output_folder=output_folder, hide_output=True)

    print('Done')


def monte_carlo():
    par_bounds = {'p_Am': (10, 1e4),
                  'kap_X': (0, 1),
                  'v': (0, 1),
                  'kap': (0, 1),
                  'p_M': (1, 1e3),
                  'E_G': (1e3, 1e4),
                  'E_Hb': (1e4, 1e8),
                  'E_Hx': (1e5, 1e9),
                  'E_Hp': (1e6, 1e10),
                  't_0': (0, 287.5),
                  'k_J': 0.002,
                  'kap_R': 0.95}

    ind_pars = ['p_Am', 'kap_X']
    if not len(ind_pars):
        folder = f"../Mertolenga/Monte Carlo/None"
    else:
        folder = f"../Mertolenga/Monte Carlo/{' '.join(ind_pars)}"
    species_name = 'Bos_taurus_Mertolenga'
    template_folder = "../Mertolenga/Testing Template"
    # Data sources
    twds = TimeWeightDataSource(f"../../Data/ACBM/CSV Files/weights_clean.csv", id_col='sia', weight_col='weight',
                                age_col='age', bibkey=f'ACBM',
                                comment=f'Data from Mertolenga performance test')
    tfds = TimeCumulativeFeedDataSource(f"../../Data/ACBM/CSV Files/feed_consumption_clean.csv", id_col='sia',
                                        feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                        bibkey=f'ACBM',
                                        comment=f'Data from Mertolenga performance test')

    gen = TestingCodeGenerator(template_folder=template_folder, individual_params=ind_pars,
                               species_name=species_name)
    gen.add_data_source(twds)
    gen.add_data_source(tfds)
    gen.set_estimation_settings(n_runs=100, results_output_mode=2, pars_init_method=2, n_steps=500)

    def extra_par_filter(pet):
        W_inf = (1 + pet.omega) * pet.L_inf() ** 3
        return pet.E_Hb < pet.E_Hx < pet.E_Hp and W_inf > 398e3

    mc = MonteCarloEstimation(par_bounds=par_bounds, folder=folder, code_gen=gen,
                              extra_parameter_filter=extra_par_filter)
    mc.estimate(n_samples=100, hide_output=False)


def run_two_step_estimations_simul():
    params = ['p_Am', 'p_M', 'kap_X']
    species_name = 'Bos_taurus_Mertolenga'
    template_folder = "../Mertolenga/Templates/Two-step/Testing"
    # Data sources
    twds = TimeWeightDataSource(f"../../Data/ACBM/CSV Files/weights_clean.csv", id_col='sia', weight_col='weight',
                                age_col='age', bibkey=f'ACBM',
                                comment=f'Data from Mertolenga performance test')
    tfds = TimeCumulativeFeedDataSource(f"../../Data/ACBM/CSV Files/feed_consumption_clean.csv", id_col='sia',
                                        feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                        bibkey=f'ACBM',
                                        comment=f'Data from Mertolenga performance test')
    # wfds = WeightFeedDataSource(f"../../Data/ACBM/CSV Files/weight_intake_clean.csv", id_col='sia',
    #                             feed_col='cumul_dry', weight_col='weight',
    #                             bibkey=f"ACBM", comment=f'Data from Mertolenga performance test')
    runner = EstimationRunner()
    results = {}
    default_pars = {'p_Am': 2499,
                    'kap_X': 0.1397,
                    'v': 0.07638,
                    'kap': 0.9183,
                    'p_M': 45.6,
                    'E_G': 8874,
                    'E_Hb': 6.018e6,
                    'E_Hx': 4.785e7,
                    'E_Hp': 1.319e8,
                    't_0': 96.42}

    for nip in (2, 1, 3):
        for p_list in combinations(params, nip):
            # if p_list == ('p_Am','p_M'):
            #     continue
            print(p_list)
            gen = TestingCodeGenerator(template_folder=template_folder, individual_params=p_list,
                                       species_name=species_name)
            gen.add_data_source(twds)
            gen.add_data_source(tfds)
            # gen.add_data_source(wfds)
            gen.set_estimation_settings(n_runs=1000, results_output_mode=3, pars_init_method=2, n_steps=1000)
            output_folder = f"../Mertolenga/Two-step/{' '.join(p_list)}"
            gen.generate_code(output_folder=output_folder, default_pars=default_pars, ind_data_weight=1)

            results[' '.join(p_list)] = runner.run_estimation(output_folder, species_name, window=False,
                                                              clear_before=True, hide_output=False)


def run_two_step_estimations():
    # params = list(default_pars.keys())
    params = ['p_Am', 'kap_X', 'p_M', 'v', 'kap', 'E_G', 'E_Hb', 'E_Hx', 'E_Hp', 't_0', 'del_M', 'h_a', 'f_group']

    species_name = 'Bos_taurus_Mertolenga'

    # group_step_template_folder = "../Mertolenga/Templates/Two-step/Group Step"
    group_step_template_folder = "../Mertolenga/Templates/Two-step/Group Step f_group"
    group_step_template_folder = "../Mertolenga/Templates/Two-step/Group Step f_group w_inf tfi"

    # ind_step_template_folder = "../Mertolenga/Templates/Two-step/Individual Step Pseudo Data"
    ind_step_template_folder = "../Mertolenga/Templates/Two-step/Individual Step Pseudo Data w_inf tfi"
    # ind_step_template_folder = "../Mertolenga/Templates/Two-step/Individual Step Group Data"
    # ind_step_template_folder = "../Mertolenga/Templates/Two-step/Individual Step Group Data f_group"

    main_output_folder = "../Mertolenga/Two-step pseudo f_group w_inf tfi"
    # main_output_folder = "../Mertolenga/Two-step group"
    # main_output_folder = "../Mertolenga/Two-step pseudo f_group"

    # Data sources
    twds = TimeWeightDataSource(f"../../Data/ACBM/CSV Files/weights_clean.csv", id_col='sia', weight_col='weight',
                                age_col='age', bibkey=f'ACBM', comment=f'Data from Mertolenga performance test')
    fwds = FinalWeightDataSource(f"../../Data/ACBM/CSV Files/weights_clean.csv", id_col='sia', weight_col='weight',
                                 age_col='age', bibkey=f'ACBM', comment=f'Data from Mertolenga performance test')
    tfds = TimeCumulativeFeedDataSource(f"../../Data/ACBM/CSV Files/feed_consumption_clean.csv", id_col='sia',
                                        feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                        bibkey=f'ACBM', comment=f'Data from Mertolenga performance test')
    tfids = TotalFeedIntakeDataSource(f"../../Data/ACBM/CSV Files/feed_consumption_clean.csv", id_col='sia',
                                      feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                      bibkey=f'ACBM', comment=f'Data from Mertolenga performance test')
    # wfds = WeightFeedDataSource(f"../../Data/ACBM/CSV Files/weight_intake_clean.csv", id_col='sia',
    #                             feed_col='cumul_dry', weight_col='weight',
    #                             bibkey=f"ACBM", comment=f'Data from Mertolenga performance test')
    data = DataCollection([twds, fwds, tfds, tfids])

    estimator = TwoStepEstimator(pars=params, species_name=species_name,
                                 group_step_template_folder=group_step_template_folder,
                                 ind_step_template_folder=ind_step_template_folder,
                                 main_output_folder=main_output_folder,
                                 data=data)
    estimation_settings = dict(n_runs=500, results_output_mode=0, pars_init_method=2, n_steps=500, tol_simplex=1e-5)
    default_pars = estimator.group_step_estimation(estimation_settings=estimation_settings)
    print(default_pars)
    # ind_list = ['PT524148448', 'PT223802666', 'PT023396456']
    n_inds = len(twds.individuals)

    # n_ind_pars_list = (2, 1)
    n_ind_pars_list = (2, 1, 3, 4, 5, 6)
    for nip in n_ind_pars_list:
        for p_list in combinations(params[:6], nip):  # not E_G
            # p_list = ('p_M', 'E_G')
            output_folder = f"{main_output_folder}/{' '.join(p_list)}"
            # Check if estimation has already been done
            if os.path.exists(output_folder):
                if len(open(f"{output_folder}/ind_pars.csv", 'r').readlines()) == n_inds + 1:
                    continue
            estimation_settings = dict(n_runs=500, results_output_mode=0, pars_init_method=2, n_steps=500,
                                       tol_simplex=1e-5)
            estimator.ind_step_estimation(default_pars=default_pars, ind_pars=list(p_list),
                                          estimation_settings=estimation_settings,
                                          ind_list=None, hide_output=True,

                                          # Estimate with group data
                                          # species_data_weight=f"1/{len(species_data_types)}",
                                          # use_pseudo_data=False, species_data_types=species_data_types)

                                          # Estimate with pseudo data
                                          use_pseudo_data=True, pseudo_data_weight=0.1)
    estimator.runner.close()


def grid_search_two_step_group():
    params = ['p_Am', 'kap_X', 'v', 'kap', 'p_M', 'E_G', 'E_Hb', 'E_Hx', 'E_Hp', 'del_M', 'h_a', 't_0', 'f_group']
    ind_pars = ['p_Am', 'kap_X']
    species_name = 'Bos_taurus_Mertolenga'
    # group_step_template_folder = "../Mertolenga/Templates/Two-step/Group Step"
    group_step_template_folder = "../Mertolenga/Templates/Two-step/Group Step f_group"
    # ind_step_template_folder = "../Mertolenga/Templates/Two-step/Individual Step Group Data"
    ind_step_template_folder = "../Mertolenga/Templates/Two-step/Individual Step Group Data f_group"
    main_output_folder = "../Mertolenga/grid search f_group high v"

    # Data sources
    twds = TimeWeightDataSource(f"../../Data/ACBM/CSV Files/weights_clean.csv", id_col='sia', weight_col='weight',
                                age_col='age', bibkey=f'ACBM',
                                comment=f'Data from Mertolenga performance test')
    tfds = TimeCumulativeFeedDataSource(f"../../Data/ACBM/CSV Files/feed_consumption_clean.csv", id_col='sia',
                                        feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                        bibkey=f'ACBM',
                                        comment=f'Data from Mertolenga performance test')
    data = DataCollection([twds, tfds])
    n_inds = len(twds.individuals)

    estimator = TwoStepEstimator(pars=params, species_name=species_name,
                                 group_step_template_folder=group_step_template_folder,
                                 ind_step_template_folder=ind_step_template_folder,
                                 main_output_folder=main_output_folder,
                                 data=data)
    group_step_estimation_settings = dict(n_runs=500, results_output_mode=-2, pars_init_method=2, n_steps=500,
                                          tol_simplex=1e-5)
    ind_step_estimation_settings = dict(n_runs=500, results_output_mode=0, pars_init_method=2, n_steps=500,
                                        tol_simplex=1e-5)

    group_data_weights = [1 / 26, 1 / 13, 1 / 8, 13 / 52, 26 / 52]
    ind_data_weights = [1 / 8, 13 / 52, 26 / 52, 39 / 52]

    for gdw, idw in product(group_data_weights, ind_data_weights):
        print(f"\nGroup data weight: {gdw:.3f}\nIndividual data weight: {idw:.3f}")

        configuration_folder = f"{main_output_folder}/gdw {gdw:.3f} idw {idw:.3f}"
        estimator.main_output_folder = configuration_folder

        # Group step
        # Check if the group step has already been performed
        if not os.path.exists(f"{configuration_folder}/Group Step"):
            default_pars = estimator.group_step_estimation(estimation_settings=group_step_estimation_settings,
                                                           ind_data_weight=idw,
                                                           hide_output=True)
        else:
            all_pars = estimator.runner.fetch_pars_from_mat_file(run_files_dir=f"{configuration_folder}/Group Step",
                                                                 species_name=species_name)
            default_pars = estimator.get_group_pars_from_all_pars(all_pars)
        print(default_pars)

        # Individual step
        # Check if individual step is complete
        ind_step_folder = f"{configuration_folder}/{' '.join(ind_pars)}"
        if os.path.exists(ind_step_folder):
            if len(open(f"{ind_step_folder}/ind_pars.csv", 'r').readlines()) == n_inds + 1:
                continue
        estimator.ind_step_estimation(default_pars=default_pars, ind_pars=ind_pars,
                                      estimation_settings=ind_step_estimation_settings,
                                      ind_list=None,
                                      species_data_weight=gdw, species_data_types=group_data_types,
                                      use_pseudo_data=False,
                                      hide_output=True)


def grid_search_two_step_pseudo():
    params = ['p_Am', 'kap_X', 'v', 'kap', 'p_M', 'E_G', 'E_Hb', 'E_Hx', 'E_Hp', 'del_M', 'h_a', 't_0', 'f_group']
    # ind_pars = ['p_Am', 'kap_X']
    # ind_pars = ['kap_X', 'p_M']
    ind_pars = ['p_Am', 'kap_X', 'p_M', 'v', 'kap']
    species_name = 'Bos_taurus_Mertolenga'
    # group_step_template_folder = "../Mertolenga/Templates/Two-step/Group Step"
    group_step_template_folder = "../Mertolenga/Templates/Two-step/Group Step f_group"
    ind_step_template_folder = "../Mertolenga/Templates/Two-step/Individual Step Pseudo Data"
    main_output_folder = "../Mertolenga/grid search"
    group_steps_folder = f"{main_output_folder}/Group Steps"
    if not os.path.exists(group_steps_folder):
        os.makedirs(group_steps_folder)

    # Data sources
    twds = TimeWeightDataSource(f"../../Data/ACBM/CSV Files/weights_clean.csv", id_col='sia', weight_col='weight',
                                age_col='age', bibkey=f'ACBM',
                                comment=f'Data from Mertolenga performance test')
    tfds = TimeCumulativeFeedDataSource(f"../../Data/ACBM/CSV Files/feed_consumption_clean.csv", id_col='sia',
                                        feed_col='cumul_dry', age_col='age', weight_data_source=twds,
                                        bibkey=f'ACBM',
                                        comment=f'Data from Mertolenga performance test')
    data = DataCollection([twds, tfds])
    n_inds = len(twds.individuals)

    estimator = TwoStepEstimator(pars=params, species_name=species_name,
                                 group_step_template_folder=group_step_template_folder,
                                 ind_step_template_folder=ind_step_template_folder,
                                 main_output_folder=main_output_folder,
                                 data=data)
    group_step_estimation_settings = dict(n_runs=500, results_output_mode=-2, pars_init_method=2, n_steps=500,
                                          tol_simplex=1e-5)
    ind_step_estimation_settings = dict(n_runs=500, results_output_mode=0, pars_init_method=2, n_steps=500,
                                        tol_simplex=1e-5)

    pseudo_data_weights = [0.006, 0.012, 0.025, 0.05, 0.1, 0.25, 0.5]
    ind_data_weights = [1 / 52, 1 / 16, 1 / 8, 13 / 52, 26 / 52, 39 / 52, 1]

    for pdw, idw in product(pseudo_data_weights, ind_data_weights):

        print(f"\nPseudo data weight: {pdw:.3f}\nIndividual data weight: {idw:.3f}")

        configuration_folder = f"{main_output_folder}/pdw {pdw:.3f} idw {idw:.3f}"
        estimator.main_output_folder = configuration_folder

        # Group step
        # Check if the group step has already been performed
        if not os.path.exists(f"{configuration_folder}/Group Step"):
            group_step_estimation = f"{group_steps_folder}/idw {idw:.3f}"
            # If the group step is not saved, run and save in the group steps folder
            if not os.path.exists(group_step_estimation):
                default_pars = estimator.group_step_estimation(estimation_settings=group_step_estimation_settings,
                                                               ind_data_weight=idw,
                                                               output_folder=group_step_estimation,
                                                               hide_output=True)
            # If it is saved, then fetch the parameters
            else:
                all_pars = estimator.runner.fetch_pars_from_mat_file(run_files_dir=group_step_estimation,
                                                                     species_name=species_name)
                default_pars = estimator.get_group_pars_from_all_pars(all_pars)
            # Then copy to the configuration folder
            shutil.copytree(group_step_estimation, f"{configuration_folder}/Group Step")
        else:
            all_pars = estimator.runner.fetch_pars_from_mat_file(run_files_dir=f"{configuration_folder}/Group Step",
                                                                 species_name=species_name)
            default_pars = estimator.get_group_pars_from_all_pars(all_pars)
        print(default_pars)

        # Individual step
        redo_individual_step = False
        estimator.main_output_folder = configuration_folder
        # Check if individual step is complete
        ind_step_folder = f"{configuration_folder}/{' '.join(ind_pars)}"
        if os.path.exists(ind_step_folder) and not redo_individual_step:
            if len(open(f"{ind_step_folder}/ind_pars.csv", 'r').readlines()) == n_inds + 1:
                continue
        estimator.ind_step_estimation(default_pars=default_pars, ind_pars=ind_pars,
                                      estimation_settings=ind_step_estimation_settings,
                                      ind_list=None,
                                      pseudo_data_weight=pdw,
                                      use_pseudo_data=True,
                                      hide_output=True)


def compile_results_from_two_step_estimation():
    main_output_folder = "../Mertolenga/Two-step pseudo f_group w_inf tfi"

    # Pars file
    pars = ['E_G', 'kap', 'kap_X', 'p_Am', 'p_M', 'v']

    par_files = {p: open(f"{main_output_folder}/Analysis/{p}_dist.csv", 'w') for p in pars}
    par_dev_files = {p: open(f"{main_output_folder}/Analysis/{p}_dev.csv", 'w') for p in pars}
    for p, f in par_files.items():
        print(f"ind_pars,mean,std,mad,cv,qcd,skew,kurt", file=f)
    for p, f in par_dev_files.items():
        print(f"ind_pars,mean,std,mad,cv,qcd,skew,kurt", file=f)
    # Error file
    data_sources = ['tW', 'tCX']
    error_summary = open(f"{main_output_folder}/Analysis/error_summary.csv", 'w')
    header = f"ind_pars,loss,loss_avg,{','.join([f'{ds}_avg,{ds}_max,{ds}_ngd' for ds in data_sources])}"
    if len(group_data_types):
        header += ",grp_data_avg"
    print(header, file=error_summary)
    for estim in os.listdir(main_output_folder):
        estim_folder = f"{main_output_folder}/{estim}"
        if estim == 'Group Step' or estim == 'Analysis' or not os.path.isdir(estim_folder):
            continue
        else:
            ind_pars = estim.split()

        # Compute error stats
        error_df = pd.read_csv(f"{estim_folder}/errors.csv", index_col='id')
        line = f"{estim} ,{error_df['loss'].sum():.5f},{error_df['loss'].mean() / len(data_sources):.5f}"
        for ds in data_sources:
            line += f",{error_df[ds].mean():.5f},{error_df[ds].max():.5f},{(error_df[ds] < 0.05).sum()}"
        if len(group_data_types):
            group_data_avg = np.mean([error_df[d0].mean() for d0 in group_data_types])
            line += f",{group_data_avg:.5f}"
        print(line, file=error_summary)

        # Compute par distributions
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
            print(f"{estim} ,{mean:.6f},{std:.6f},{mad:.6f},{cv:.6f},{qcd:.6f},{skew:.6f},{kurt:.6f}",
                  file=par_files[p])

            par_devs = np.abs(par_vals - default_pars[p]) / default_pars[p]
            mean = par_devs.mean()
            std = par_devs.std()
            mad = np.median(np.abs(par_devs - par_devs.median()))
            cv = std / mean
            q1 = par_devs.quantile(0.25)
            q3 = par_devs.quantile(0.75)
            qcd = (q3 - q1) / (q1 + q3)
            skew = par_devs.skew()
            kurt = par_devs.kurt()
            print(f"{estim} ,{mean:.6f},{std:.6f},{mad:.6f},{cv:.6f},{qcd:.6f},{skew:.6f},{kurt:.6f}",
                  file=par_dev_files[p])

    error_summary.close()
    for p, f in par_files.items():
        f.close()
    for p, f in par_dev_files.items():
        f.close()


if __name__ == '__main__':
    # <====     Angus Performance Test 2022   ======>
    # species_name = 'Bos_taurus_Angus'
    # group_step_template_folder = "../Angus/Templates/Angus Performance Test 2022/Group Step"
    # output_folder = "../Angus/Angus Performance Test 2022/estimate from scratch"
    # bibkey = 'AngusPT'
    # comment = 'Data from Angus 2022 Performance Test'
    #
    # # Data sources
    # twds = TimeWeightDataSource(f"../../../Data/Angus/Angus PT/CSV Files/weights_2022.csv",
    #                             id_col='collar_id', weight_col='weight', date_col='date',
    #                             bibkey=bibkey, comment=comment)
    # tfds = TimeFeedDataSource(f"../../../Data/Angus/Angus PT/CSV Files/feed_intake_2022.csv",
    #                             id_col='collar_id', date_col='date', feed_col='dry_intake', weight_data_source=twds,
    #                             bibkey=bibkey, comment=comment)
    # data = DataCollection([twds, tfds])
    #
    # code_generator = TrainingCodeGenerator(group_step_template_folder, [], species_name, data)
    #
    # estimation_settings = dict(n_runs=500, results_output_mode=3, pars_init_method=2, n_steps=500, tol_simplex=1e-4)
    # code_generator.set_estimation_settings(**estimation_settings)
    #
    # code_generator.generate_code(output_folder=output_folder)


    # <====     GREENBEEF TRIAL 1   ======>
    species_name = 'Bos_taurus_Angus'
    params = ['p_Am', 'kap_X', 'xi_C', 'kap_P', 'p_M', 'v', 'kap', 'E_G', 'E_Hb', 'E_Hx', 'E_Hp', 't_0', 'del_M', 'h_a']
    group_pars = ['p_Am_CTRL', 'kap_X_CTRL', 'xi_C_CTRL', 'kap_P_CTRL',
                  'p_Am_TMR', 'kap_X_TMR', 'xi_C_TMR', 'kap_P_TMR']
    params += group_pars
    group_step_template_folder = "../Angus/Templates/GreenBeef Trial 1/Group Step JXGrp CO2 CH4"
    ind_step_template_folder = "../Angus/Templates/GreenBeef Trial 1/Individual Step tW JXGrp CO2 CH4"
    main_output_folder = "../Angus/GreenBeef Trial 1/Two-step pseudo p_Am kap_X xi_C kap_P psd 001"
    bibkey = 'GreenBeefTrial1'
    comment = 'Data from GreenBeef trial'

    # Data sources
    twds = TimeWeightDataSource(f"../../../Data/Angus/Greenbeef/CSV Files/greenbeef_weights.csv",
                                id_col='sia', weight_col='weight', date_col='date',
                                bibkey=bibkey, comment=comment)

    gtfds = TimeFeedGroupDataSource(f"../../../Data/Angus/Greenbeef/CSV Files/greenbeef_feed_intake_pen.csv",
                                   group_col='pen', feed_col='dry_intake', date_col='date', weight_data_source=twds,
                                   bibkey=bibkey, comment=comment)

    tmds = TimeCH4DataSource(f"../../../Data/Angus/Greenbeef/CSV Files/greenbeef_emissions.csv",
                             id_col='sia', methane_col='CH4', date_col='date', weight_data_source=twds,
                             bibkey=bibkey, comment=comment)

    tco2ds = TimeCO2DataSource(f"../../../Data/Angus/Greenbeef/CSV Files/greenbeef_emissions.csv",
                               id_col='sia', co2_col='CO2', date_col='date', weight_data_source=twds,
                               bibkey=bibkey, comment=comment)

    data = DataCollection([twds, gtfds, tmds, tco2ds])

    estimator = TwoStepEstimator(pars=params, species_name=species_name,
                                 group_step_template_folder=group_step_template_folder,
                                 ind_step_template_folder=ind_step_template_folder,
                                 main_output_folder=main_output_folder,
                                 data=data)
    estimation_settings = dict(n_runs=500, results_output_mode=0, pars_init_method=2, n_steps=500, tol_simplex=1e-4)
    # default_pars = estimator.group_step_estimation(estimation_settings=estimation_settings)
    default_pars = {'p_Am_CTRL': 4706,
                    'p_Am_TMR': 4360,
                    'kap_X_CTRL': 0.1621,
                    'kap_X_TMR': 0.1455,
                    'kap_P_CTRL': 0.2349,
                    'kap_P_TMR': 0.3413,
                    'xi_C_CTRL': 0.03449,
                    'xi_C_TMR': 0.06195,
                    'p_M': 76.01,
                    'v': 0.07304,
                    'kap': 0.9681,
                    'E_G': 7831}

    print(default_pars)
    n_inds = len(twds.individuals)

    n_ind_pars_list = (1, 2, 3, 4)
    pars_to_free = ['p_Am', 'kap_X', 'xi_C', 'kap_P', 'p_M', 'v']
    for nip in n_ind_pars_list:
        for p_list in combinations(pars_to_free, nip):
            # p_list = ('p_M', 'E_G')
            output_folder = f"{main_output_folder}/{' '.join(p_list)}"
            # Check if estimation has already been done
            if os.path.exists(f"{output_folder}/ind_pars.csv"):
                if len(open(f"{output_folder}/ind_pars.csv", 'r').readlines()) == n_inds + 1:
                    continue
            estimation_settings = dict(n_runs=500, results_output_mode=0, pars_init_method=2, n_steps=500,
                                       tol_simplex=1e-5)
            estimator.ind_step_estimation(default_pars=default_pars, ind_pars=list(p_list),
                                          estimation_settings=estimation_settings,
                                          ind_groups_list=None, hide_output=True,

                                          # Estimate with group data
                                          # species_data_weight=f"1/{len(species_data_types)}",
                                          # use_pseudo_data=False, species_data_types=species_data_types)

                                          # Estimate with pseudo data
                                          use_pseudo_data=True, pseudo_data_weight=0.01)
    # estimator.runner.close()

    compile_results(estimator, pars_to_get_stats=pars_to_free)

    # group_step_code_generator = TrainingCodeGenerator(group_step_template_folder, [], species_name, data)
    # estimation_settings = dict(n_runs=500, results_output_mode=3, pars_init_method=2, n_steps=500, tol_simplex=1e-5)
    # group_step_code_generator.set_estimation_settings(**estimation_settings)
    # group_step_code_generator.generate_code(output_folder="../Angus/GreenBeef Trial/Group Step")
