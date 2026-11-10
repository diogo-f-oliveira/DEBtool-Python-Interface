import argparse

from DEBtoolPyIF import MultiTierResults
from examples.Bos_taurus_Angus.data import load_data
from examples.Bos_taurus_Angus.tier_structure import create_tier_structure
from examples.Bos_taurus_Angus.tier_structure import ESTIMATION_FOLDER, SPECIES_NAME

INITIAL_PARS = {
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

ESTIMATION_SETTINGS_PROFILES = {
    'fast': FAST_TEST_ESTIMATION_SETTINGS,
    'end-to-end': END_TO_END_ESTIMATION_SETTINGS,
}


def load_estimation_results(output_folder=ESTIMATION_FOLDER):
    """
    Load persisted estimation results for this example.

    Results are intentionally independent from the original DataCollection objects. Use this helper for inspecting
    saved parameter tables, errors, metadata, and summaries without reconstructing a runnable multitier workflow.
    """
    return MultiTierResults.from_folder(output_folder=output_folder, species_name=SPECIES_NAME)


def resolve_estimation_settings(profile_name='fast'):
    """Return the estimation settings for a named Angus example profile."""
    try:
        return ESTIMATION_SETTINGS_PROFILES[profile_name]
    except KeyError as exc:
        valid_profiles = ', '.join(sorted(ESTIMATION_SETTINGS_PROFILES))
        raise ValueError(
            f"Unknown estimation settings profile {profile_name!r}. "
            f"Valid profiles are: {valid_profiles}."
        ) from exc


def run_multitier_estimation(multitier, estimation_settings=FAST_TEST_ESTIMATION_SETTINGS):
    """Run estimation for all tiers in the multitier structure."""
    for tier_name in multitier.tiers.keys():
        initial_pars = INITIAL_PARS if tier_name == 'breed' else None
        multitier.tiers[tier_name].estimate(
            save_results=True,
            print_results=False,
            hide_output=True,
            estimation_settings=estimation_settings[tier_name],
            trace_output=True,
            initial_pars=initial_pars,
        )


def build_parser():
    """Build the command-line parser for this example module."""
    parser = argparse.ArgumentParser(
        description='Run the Bos taurus Angus multitier estimation example.',
    )
    parser.add_argument(
        '--settings',
        choices=sorted(ESTIMATION_SETTINGS_PROFILES),
        default='fast',
        help='Estimation settings profile to use. Defaults to fast.',
    )
    return parser


def main(argv=None):
    """Run the Angus example from the command line."""
    args = build_parser().parse_args(argv)
    estimation_settings = resolve_estimation_settings(args.settings)

    data = load_data('examples/Bos_taurus_Angus/data')
    tier_structure = create_tier_structure(data, matlab_session='auto')
    run_multitier_estimation(tier_structure, estimation_settings=estimation_settings)
    print('Done')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
