from examples.Bos_taurus_Angus.data import load_data
from examples.Bos_taurus_Angus.tier_structure import create_tier_structure

FAST_TEST_ESTIMATION_SETTINGS = {
    'breed': dict(
        n_runs=3,
        results_output_mode=0,
        n_steps=50,
        n_evals=50000,
        pars_init_method=2,
        tol_simplex=1e-4,
        tol_restart=1e-4,
    ),
    'diet': dict(
        n_runs=3,
        results_output_mode=0,
        n_steps=50,
        n_evals=50000,
        pars_init_method=2,
        tol_simplex=1e-4,
        tol_restart=1e-4,
    ),
    'individual': dict(
        n_runs=3,
        results_output_mode=0,
        n_steps=50,
        n_evals=50000,
        pars_init_method=2,
        tol_simplex=1e-4,
        tol_restart=1e-4,
    ),
}

END_TO_END_ESTIMATION_SETTINGS = {
    'breed': dict(
        n_runs=50,
        results_output_mode=3,
        n_steps=500,
        n_evals=50000,
        pars_init_method=2,
        tol_simplex=1e-4,
        tol_restart=1e-4,
    ),
    'diet': dict(
        n_runs=10,
        results_output_mode=0,
        n_steps=500,
        n_evals=50000,
        pars_init_method=2,
        tol_simplex=1e-4,
        tol_restart=1e-4,
    ),
    'individual': dict(
        n_runs=10,
        results_output_mode=0,
        n_steps=500,
        n_evals=50000,
        pars_init_method=2,
        tol_simplex=1e-4,
        tol_restart=1e-4,
    ),
}


def load_estimation_results(multitier):
    """
    Load estimation results for all tiers in the multitier structure.

    Returns a per-tier summary with the loaded metadata and timing information so callers can inspect the saved
    estimation outputs without needing to manually walk each tier object.
    """
    loaded_results = {}
    for tier_name in multitier.tier_names:
        tier = multitier.tiers[tier_name]
        tier.load_results()
        loaded_results[tier_name] = {
            'result_metadata': tier.result_metadata,
            'estimation_settings': tier.estimation_settings,
            'estimation_start_time': tier.estim_start_time,
            'estimation_end_time': tier.estim_end_time,
            'elapsed_duration_seconds': (
                None if tier.result_metadata is None else tier.result_metadata.get('elapsed_duration_seconds')
            ),
            'estimation_iterations': list(tier.estimation_iterations),
        }
    return loaded_results


def run_multitier_estimation(multitier, estimation_settings=FAST_TEST_ESTIMATION_SETTINGS):
    """Run estimation for all tiers in the multitier structure."""
    for tier_name in multitier.tiers.keys():
        print(f"Running estimation for tier: {tier_name}")
        multitier.tiers[tier_name].estimate(
            save_results=True,
            print_results=False,
            hide_output=False,
            estimation_settings=estimation_settings[tier_name],
        )


if __name__ == '__main__':
    # Create data and multitier structure and run the minimal example
    data = load_data('examples/Bos_taurus_Angus/data')
    multitier = create_tier_structure(data, matlab_session='auto')
    run_multitier_estimation(multitier, estimation_settings=END_TO_END_ESTIMATION_SETTINGS)
    # run_multitier_estimation(multitier, estimation_settings=FAST_TEST_ESTIMATION_SETTINGS)
    print('Done')
