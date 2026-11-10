from pathlib import Path

from DEBtoolPyIF.data_sources.collection import DataCollection
from DEBtoolPyIF.multitier import MultiTierStructure, TierHierarchy
from examples.Bos_taurus_Angus.templates import build_estimation_templates

HERE = Path(__file__).resolve().parent
ESTIMATION_FOLDER = HERE / 'multitier'
BASE_TEMPLATE_FOLDER = HERE / 'templates'

SPECIES_NAME = 'Bos_taurus_Angus'
TIER_NAMES = ['breed', 'diet', 'individual']
BREED_TIER_PARS = [
    'p_Am',
    'kap_X',
    'kap_P',
    'p_M',
    'v',
    'kap',
    'E_G',
    'E_Hb',
    'E_Hx',
    'E_Hp',
    'h_a',
    't_0',
    'del_M',
    'p_Am_f',
    'E_Hp_f',
]


def generate_entity_hierarchy(data: DataCollection) -> TierHierarchy:
    """Create the TierHierarchy used by the example."""
    paths = []
    twds = data.entity_data_sources['greenbeef_1_weights_tW']
    ind_list = list(twds.entities)
    for ind_id in ind_list:
        ind_data = twds.get_entity_data(ind_id).iloc[0]
        paths.append({'breed': 'male', 'diet': f"{ind_data['diet']}", 'individual': ind_id})
    return TierHierarchy.from_paths(tier_names=TIER_NAMES, paths=paths)


def create_tier_structure(data, matlab_session='auto', output_folder=ESTIMATION_FOLDER) -> MultiTierStructure:
    """Create and return a MultiTierStructure from example data."""
    entity_hierarchy = generate_entity_hierarchy(data['individual'])

    tier_pars = {
        'breed': BREED_TIER_PARS,
        'diet': ['p_Am', 'kap_X', 'kap_P'],
        'individual': ['p_Am', 'kap_X']
    }

    estimation_templates = build_estimation_templates(
        base_template_folder=BASE_TEMPLATE_FOLDER,
        tier_names=TIER_NAMES,
        species_name=SPECIES_NAME,
    )

    multitier = MultiTierStructure(species_name=SPECIES_NAME, entity_hierarchy=entity_hierarchy, data=data,
                                   tier_pars=tier_pars,
                                   estimation_templates=estimation_templates,
                                   output_folder=output_folder,
                                   matlab_session=matlab_session)

    return multitier
