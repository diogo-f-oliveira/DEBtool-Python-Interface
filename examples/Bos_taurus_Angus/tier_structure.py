import numpy as np
import pandas as pd
from pathlib import Path

from DEBtoolPyIF.data_sources.collection import DataCollection
from DEBtoolPyIF.multitier.procedure import MultiTierStructure


HERE = Path(__file__).resolve().parent
ESTIMATION_FOLDER = str(HERE / 'multitier')
BASE_TEMPLATE_FOLDER = str(HERE / 'templates')

TIER_NAMES = ['breed', 'diet', 'individual']


def generate_entity_vs_tier_df(data: DataCollection) -> pd.DataFrame:
    """Create the entity_vs_tier DataFrame used by the example."""
    entity_vs_tier_df = pd.DataFrame(
        index=pd.MultiIndex(levels=[[], []], codes=[[], []], names=['tier', 'entity']),
        columns=TIER_NAMES,
    )

    # Breed
    entity_vs_tier_df.loc[('breed', 'male'), 'breed'] = 'male'
    # Diets
    for diet in ['CTRL', 'TMR']:
        entity_vs_tier_df.loc[('diet', diet), :] = ['male', diet, np.nan]
    # Individuals
    twds = data.entity_data_sources['greenbeef_1_weights_tW']
    ind_list = list(twds.entities)
    for ind_id in ind_list:
        ind_data = twds.get_entity_data(ind_id).iloc[0]
        entity_vs_tier_df.loc[('individual', ind_id), :] = ['male', f"{ind_data['diet']}", ind_id]

    return entity_vs_tier_df


def create_tier_structure(data, matlab_session='auto') -> MultiTierStructure:
    """Create and return a MultiTierStructure from example data."""
    entity_vs_tier_df = generate_entity_vs_tier_df(data['individual'])

    initial_pars = {
        'p_Am': 5000,
        'kap_X': 0.2,
        'kap_P': 0.1,
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

    tier_pars = {
        'breed': list(initial_pars.keys()),
        'diet': ['p_Am', 'kap_X', 'kap_P'],
        'individual': ['p_Am', 'kap_X']
    }

    multitier = MultiTierStructure(species_name='Bos_taurus_Angus', entity_vs_tier=entity_vs_tier_df, data=data,
                                   pars=initial_pars,
                                   tier_pars=tier_pars,
                                   template_folder=BASE_TEMPLATE_FOLDER,
                                   output_folder=ESTIMATION_FOLDER,
                                   matlab_session=matlab_session)

    return multitier
