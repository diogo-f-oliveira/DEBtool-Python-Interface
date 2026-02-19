from examples.Bos_taurus_Angus.data import load_data
from examples.Bos_taurus_Angus.tier_structure import create_tier_structure


def load_estimation_results(multitier):
    """Load estimation results for all tiers in the multitier structure."""
    for tier_name in multitier.tiers.keys():
        multitier.tiers[tier_name].load_results()


def run_estimation(multitier):
    """Run estimation for all tiers in the multitier structure."""
    for tier_name in multitier.tiers.keys():
        print(f"Running estimation for tier: {tier_name}")
        multitier.tiers[tier_name].run_estimation()


if __name__ == '__main__':
    # Create data and multitier structure and run the minimal example
    data = load_data('examples/Bos_taurus_Angus/data')
    multitier = create_tier_structure(data, matlab_session='ignore')



    print('Done')
