from examples.Bos_taurus_Angus.data import load_data
from examples.Bos_taurus_Angus.tier_structure import create_tier_structure


FAST_TEST_ESTIMATION_SETTINGS = {
    'breed': dict(n_runs=3, results_output_mode=0, n_steps=50, pars_init_method=2, tol_simplex=1e-4),
    'diet': dict(n_runs=3, results_output_mode=0, n_steps=50, pars_init_method=2, tol_simplex=1e-4),
    'individual': dict(n_runs=3, results_output_mode=0, n_steps=50, pars_init_method=2, tol_simplex=1e-4),
}

END_TO_END_ESTIMATION_SETTINGS = {
    'breed': dict(n_runs=50, results_output_mode=3, n_steps=500, pars_init_method=2, tol_simplex=1e-4),
    'diet': dict(n_runs=10, results_output_mode=0, n_steps=500, pars_init_method=2, tol_simplex=1e-4),
    'individual': dict(n_runs=10, results_output_mode=0, n_steps=500, pars_init_method=2, tol_simplex=1e-4),
}


def load_estimation_results(multitier):
    """Load estimation results for all tiers in the multitier structure."""
    for tier_name in multitier.tiers.keys():
        multitier.tiers[tier_name].load_results()


def run_multitier_estimation(multitier, estimation_settings=FAST_TEST_ESTIMATION_SETTINGS):
    """Run estimation for all tiers in the multitier structure."""
    for tier_name in multitier.tiers.keys():
        print(f"Running estimation for tier: {tier_name}")
        multitier.tiers[tier_name].estimate(
            save_results=True,
            print_results=False,
            hide_output=True,
            estimation_settings=estimation_settings[tier_name],
        )


if __name__ == '__main__':
    # Create data and multitier structure and run the minimal example
    data = load_data('examples/Bos_taurus_Angus/data')
    multitier = create_tier_structure(data, matlab_session='ignore')
    run_multitier_estimation(multitier, estimation_settings=END_TO_END_ESTIMATION_SETTINGS)

    print('Done')
