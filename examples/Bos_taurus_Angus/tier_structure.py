from pathlib import Path

from DEBtoolPyIF.data_sources.collection import DataCollection
from DEBtoolPyIF.multitier import MultiTierStructure, TierHierarchy
from examples.Bos_taurus_Angus.templates import build_estimation_templates

HERE = Path(__file__).resolve().parent
ESTIMATION_FOLDER = HERE / 'multitier'
BASE_TEMPLATE_FOLDER = HERE / 'templates'

SPECIES_NAME = 'Bos_taurus_Angus'
TIER_NAMES = ['breed', 'diet', 'individual']


def generate_entity_hierarchy(data: DataCollection) -> TierHierarchy:
    """Create the TierHierarchy used by the example."""
    paths = []
    twds = data.entity_data_sources['greenbeef_1_weights_tW']
    ind_list = list(twds.entities)
    for ind_id in ind_list:
        ind_data = twds.get_entity_data(ind_id).iloc[0]
        paths.append({'breed': 'male', 'diet': f"{ind_data['diet']}", 'individual': ind_id})
    return TierHierarchy.from_paths(tier_names=TIER_NAMES, paths=paths)


def create_tier_structure(data, matlab_session='auto') -> MultiTierStructure:
    """Create and return a MultiTierStructure from example data."""
    entity_hierarchy = generate_entity_hierarchy(data['individual'])

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

    estimation_templates = build_estimation_templates(
        base_template_folder=BASE_TEMPLATE_FOLDER,
        tier_names=TIER_NAMES,
        species_name=SPECIES_NAME,
    )

    multitier = MultiTierStructure(species_name=SPECIES_NAME, entity_hierarchy=entity_hierarchy, data=data,
                                   pars=initial_pars,
                                   tier_pars=tier_pars,
                                   estimation_templates=estimation_templates,
                                   output_folder=ESTIMATION_FOLDER,
                                   matlab_session=matlab_session)

    return multitier
