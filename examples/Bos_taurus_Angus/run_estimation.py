import pandas as pd
from src.DEBtoolPyIF.data_sources.collection import DataCollection
from src.DEBtoolPyIF.data_sources.individual import TimeWeightDataSource
from src.DEBtoolPyIF.data_sources.group import GroupTimeFeedDataSource
from src.DEBtoolPyIF.multitier.procedure import MultiTierStructure
from src.DEBtoolPyIF.utils.data_formatter import format_dict_data, format_aux_data, format_meta_data

from itertools import combinations
import os

DATA_FOLDER = 'data'
ESTIMATION_FOLDER = 'multitier'
BASE_TEMPLATE_FOLDER = 'templates'


def load_data():
    # <====     GREENBEEF TRIAL 1   ======>
    bibkey = 'GreenBeefTrial1'
    comment = 'Data from GreenBeef trial 1'
    prefix = 'Pen'

    # Data sources
    twds = TimeWeightDataSource(f"{DATA_FOLDER}/greenbeef_1_weights.csv",
                                id_col='sia', weight_col='weight', date_col='date',
                                bibkey=bibkey, comment=comment)

    gtfds = GroupTimeFeedDataSource(f"{DATA_FOLDER}/greenbeef_1_feed_intake_pen.csv",
                                    id_col='pen', feed_col='dry_intake', date_col='date',
                                    weight_data_source=twds,
                                    prefix=prefix, bibkey=bibkey, comment=comment)

    return DataCollection([twds, gtfds])


def generate_ind_tiers(data: DataCollection):
    ind_tiers = pd.DataFrame(columns=['breed', 'diet', 'individual'])

    # Trial 1
    twds = data.ind_data_sources['greenbeef_1_weights_tW']
    ind_list = list(twds.individuals)
    for ind_id in ind_list:
        ind_data = twds.get_ind_data(ind_id).iloc[0]
        ind_tiers.loc[ind_id] = ['male', f"{ind_data['diet']}", ind_id]

    ind_tiers.to_csv(f'{ESTIMATION_FOLDER}/ind_tiers.csv')
    return ind_tiers


def create_tier_structure():
    data = load_data()
    ind_tiers = generate_ind_tiers(data)

    template_folders = {
        'breed': f'{BASE_TEMPLATE_FOLDER}/breed',
        'diet': f'{BASE_TEMPLATE_FOLDER}/diet',
        'individual': f'{BASE_TEMPLATE_FOLDER}/individual'
    }
    # Initial parameter values for first tier 'breed'. Used with pars_init_method=2
    initial_pars = {
        'p_Am': 5000,
        'kap_X': 0.2,
        'p_M': 80,
        'v': 0.05,
        'kap': 0.97,
        'E_G': 7800,
        'E_Hb': 2e+6,
        'E_Hx': 2e+7,
        'E_Hp': 6e+7,
        'h_a': 5e-10,
        't_0': 80,
        'del_M': 0.15,
        'p_Am_f': 4500,
        'E_Hp_f': 6e+7,
    }
    # Parameters that are estimated in each tier
    tier_pars = {
        'breed': list(initial_pars.keys()),
        'diet': ['p_Am', 'kap_X'],
        'individual': ['p_Am', 'kap_X']
    }

    estimation_settings = {
        'breed': dict(n_runs=5, results_output_mode=-3, n_steps=500, pars_init_method=2, tol_fun=1e-4),
        'diet': dict(n_runs=5, results_output_mode=0, n_steps=500, pars_init_method=2, tol_fun=1e-4),
        'individual': dict(n_runs=5, results_output_mode=0, n_steps=500, pars_init_method=2, tol_fun=1e-4)
    }
    tier_output_folders = {
        'breed': 'breed',
        'diet': 'diet',
        'individual': 'individual'
    }

    multitier = MultiTierStructure(species_name='Bos_taurus_Angus', ind_tiers=ind_tiers, data=data,
                                   pars=initial_pars,
                                   tier_pars=tier_pars,
                                   template_folders=template_folders,
                                   output_folder=ESTIMATION_FOLDER,
                                   estimation_settings=estimation_settings,
                                   tier_output_folders=tier_output_folders,
                                   matlab_session='find')

    return multitier


if __name__ == '__main__':
    multitier = create_tier_structure()

    # multitier.tiers['breed'].estimate(hide_output=True)
    multitier.tiers['breed'].load_results()
    # multitier.tiers['breed'].fetch_pars(tier_sample_list=['male'])
    # multitier.tiers['breed'].fetch_errors(tier_sample_list=['male'])
    # multitier.tiers['breed'].save_results()
    # save_extra_data('breed')
    multitier.tiers['breed'].print_pars(tier_sample_list=['male'])

    dy_ts_list = multitier.tiers['diet'].tier_sample_list
    multitier.tiers['diet'].estimate(hide_output=True)
    # multitier.tiers['diet'].load_results()
    # multitier.tiers['diet'].fetch_pars(tier_sample_list=dy_ts_list)
    # multitier.tiers['diet'].fetch_errors(tier_sample_list=dy_ts_list)
    # multitier.tiers['diet'].save_results()
    multitier.tiers['diet'].print_pars(tier_sample_list=dy_ts_list)

    ind_list = multitier.tiers['individual'].tier_sample_list
    multitier.tiers['individual'].estimate()
    multitier.tiers['individual'].print_pars(tier_sample_list=ind_list)

    print('Done')
