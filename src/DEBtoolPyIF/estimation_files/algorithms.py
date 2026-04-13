"""Skeleton run.m algorithm templates."""

from __future__ import annotations

from .run import RunProgrammaticTemplate, RunSection
from .run_sections import *
from .run_options import *


class NelderMead(RunProgrammaticTemplate):
    """Skeleton template for a Nelder-Mead run.m algorithm."""
    attribute_to_option_class = {
        'n_steps': SetMaxStepNumberOption,
        'n_evals': SetMaxFunEvalsOption,
        'simplex_size': SetSimplexSizeOption,
        'tol_simplex': SetTolSimplexOption,
        'pars_init_method': SetParsInitMethodOption,
        'results_output_mode': SetResultsOutputOption,
    }

    def __init__(self, *,
                 n_steps: int | None = None,
                 n_evals: int | None = None,
                 simplex_size: float | None = None,
                 tol_simplex: float | None = None,
                 pars_init_method: int | None = None,
                 results_output_mode: int | None = None,
                 save_predictions: bool = True,
                 ) -> None:
        sections = (
            RunSetupSection(),
            SetEstimOptionsSection(options=(
                SetMethodOption("nm"),
                self._resolve_alg_setting('n_steps', n_steps),
                self._resolve_alg_setting('n_evals', n_evals),
                self._resolve_alg_setting('simplex_size', simplex_size),
                self._resolve_alg_setting('tol_simplex', tol_simplex),
                self._resolve_alg_setting('pars_init_method', pars_init_method),
                self._resolve_alg_setting('results_output_mode', results_output_mode),
            )),
            EstimationCallSection()
        )
        if save_predictions:
            sections += SavePredictionsSection(),

        super().__init__(sections=sections)

    def _resolve_alg_setting(self, name, value):
        if value is None:
            return self.attribute_to_option_class[name](render_key=name)
        else:
            return self.attribute_to_option_class[name](value)

    def get_estimation_settings(self):
        return


class RestartingNelderMead(RunProgrammaticTemplate):
    """Skeleton template for a restarting Nelder-Mead run.m algorithm."""

    def __init__(self, *, sections: tuple[RunSection, ...] | None = None) -> None:
        super().__init__(sections=sections)


class AlternatingRestartNelderMead(RunProgrammaticTemplate):

    def __init__(self, *, sections: tuple[RunSection, ...] | None = None) -> None:
        super().__init__(sections=sections)
