"""Run a single-species (regular Add-my-Pet style) estimation for Danio rerio with mock data.

Usage, from the repository root:

    conda run -n debtoolpyif_dev python -m examples.Danio_rerio.estimation --settings fast
"""

import argparse

from DEBtoolPyIF import EstimationRunner
from DEBtoolPyIF.estimation_files import SpeciesGenerationContext, write_estimation_files

from examples.Danio_rerio.templates import EXAMPLE_FOLDER, SPECIES_NAME, build_estimation_templates

ESTIMATION_FOLDER = EXAMPLE_FOLDER / "estimation"

# Initial values, deliberately away from the parameters used to generate the mock data.
INITIAL_PARS = {
    "z": 0.6,
    "kap_X": 0.8,
    "kap_P": 0.1,
    "v": 0.025,
    "kap": 0.7,
    "p_M": 250.0,
    "E_G": 5000.0,
    "E_Hb": 0.4,
    "E_Hp": 1500.0,
    "h_a": 5e-9,
    "del_M": 0.18,
}
FREE_PARS = ("z", "v", "kap", "p_M", "E_Hb", "E_Hp", "h_a", "del_M")

ESTIMATION_SETTINGS = {
    "fast": dict(n_steps=200, n_evals=20000, tol_simplex=1e-4, pars_init_method=2, results_output_mode=0),
    "end-to-end": dict(n_steps=5000, n_evals=50000, tol_simplex=1e-6, pars_init_method=2, results_output_mode=0),
}


def build_context(settings: str = "fast", output_folder=ESTIMATION_FOLDER) -> SpeciesGenerationContext:
    return SpeciesGenerationContext(
        species_name=SPECIES_NAME,
        output_folder=output_folder,
        full_pars_dict=dict(INITIAL_PARS),
        free_pars=FREE_PARS,
        estimation_settings=ESTIMATION_SETTINGS[settings],
    )


def run_estimation(settings: str = "fast", output_folder=ESTIMATION_FOLDER, hide_output: bool = True) -> dict:
    """Write the four species files, run DEBtool and return the estimated free parameters."""
    context = build_context(settings, output_folder)
    write_estimation_files(build_estimation_templates(), context)

    runner = EstimationRunner(estim_files_dir=context.output_folder, species_name=SPECIES_NAME)
    if not runner.run_estimation(hide_output=hide_output):
        raise RuntimeError("DEBtool estimation did not finish successfully.")
    pars = runner.fetch_pars_from_mat_file()
    return {par: pars[par] for par in FREE_PARS}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--settings", choices=sorted(ESTIMATION_SETTINGS), default="fast")
    parser.add_argument("--show-output", action="store_true", help="Show the MATLAB command window output.")
    args = parser.parse_args()

    estimated = run_estimation(args.settings, hide_output=not args.show_output)
    print(f"Estimated parameters ({args.settings}), written to {ESTIMATION_FOLDER}:")
    for par, value in estimated.items():
        print(f"  {par:6s} = {value:.6g}  (initial {INITIAL_PARS[par]:.6g})")


if __name__ == "__main__":
    main()
