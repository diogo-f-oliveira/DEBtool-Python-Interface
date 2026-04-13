"""Programmatic run.m algorithm templates."""

from __future__ import annotations

from .run import RunProgrammaticTemplate
from .run_options import (
    EstimOption,
    SetEstimOptionsSection,
    SetMaxFunEvalsOption,
    SetMaxStepNumberOption,
    SetMethodOption,
    SetParsInitMethodOption,
    SetResultsOutputOption,
    SetSimplexSizeOption,
    SetTolSimplexOption,
)
from .run_sections import EstimationCallSection, RunSection, RunSetupSection, SavePredictionsSection, \
    RestartLoopSection, GetResultsSection


class AlgorithmRunTemplate(RunProgrammaticTemplate):
    """Base class for optimizer-specific programmatic run.m templates.

    Algorithm settings supplied at construction time are rendered literally.
    Settings left as ``None`` become render-time keys resolved from
    ``context.estimation_settings``.
    """

    method: str = ""
    option_classes: dict[str, type[EstimOption]] = {}

    def __init__(
        self,
        *,
        extra_options: tuple[EstimOption, ...] = (),
        post_estimation_sections: tuple[RunSection, ...] = (),
    ) -> None:
        self.extra_options = tuple(extra_options)
        self.post_estimation_sections = tuple(post_estimation_sections)
        sections = (
            RunSetupSection(),
            SetEstimOptionsSection(options=self.build_algorithm_options()),
            *self.build_estimation_sections(),
            *self.post_estimation_sections,
        )
        super().__init__(sections=sections)

    def get_algorithm_settings(self) -> dict[str, object | None]:
        """Return public algorithm setting keys and their construction-time values."""

        return {}

    def build_algorithm_option(self, setting_key: str, value) -> EstimOption:
        """Build one typed ``estim_options`` object for a fixed or render-time value."""

        option_class = self.option_classes.get(setting_key)
        if option_class is None:
            raise ValueError(
                f"Unsupported algorithm setting '{setting_key}'. "
                f"Expected one of: {', '.join(self.option_classes)}."
            )
        if value is None:
            return option_class(render_key=setting_key)
        return option_class(value)

    def build_algorithm_options(self) -> tuple[EstimOption, ...]:
        """Build the ordered option list owned by this algorithm template."""

        return (
            SetMethodOption(self.method),
            *(
                self.build_algorithm_option(setting_key, value)
                for setting_key, value in self.get_algorithm_settings().items()
                if setting_key in self.option_classes
            ),
            *self.get_builtin_algorithm_options(),
            *self.extra_options,
        )

    def get_builtin_algorithm_options(self) -> tuple[EstimOption, ...]:
        """Return fixed options owned by the algorithm but not exposed as public settings."""

        return ()

    def build_estimation_sections(self) -> tuple[RunSection, ...]:
        """Return the section or sections that perform estimation."""

        return (EstimationCallSection(),)

    def get_render_time_settings(self) -> dict[str, None]:
        """Return settings that must be supplied through ``context.estimation_settings``."""

        return {
            setting_key: None
            for setting_key, value in self.get_algorithm_settings().items()
            if value is None
        }

    def get_fixed_settings(self) -> dict[str, object]:
        """Return settings fixed at construction time."""

        return {
            setting_key: value
            for setting_key, value in self.get_algorithm_settings().items()
            if value is not None
        }


class NelderMead(AlgorithmRunTemplate):
    """Programmatic template for a Nelder-Mead run.m algorithm."""

    method = "nm"
    option_classes = {
        "n_steps": SetMaxStepNumberOption,
        "n_evals": SetMaxFunEvalsOption,
        "simplex_size": SetSimplexSizeOption,
        "tol_simplex": SetTolSimplexOption,
        "pars_init_method": SetParsInitMethodOption,
        "results_output_mode": SetResultsOutputOption,
    }

    def __init__(
        self,
        *,
        n_steps: int | None = None,
        n_evals: int | None = None,
        simplex_size: float | None = None,
        tol_simplex: float | None = None,
        pars_init_method: int | None = None,
        results_output_mode: int | None = None,
        save_predictions: bool = True,
        extra_options: tuple[EstimOption, ...] = (),
        post_estimation_sections: tuple[RunSection, ...] | None = None,
    ) -> None:
        self._algorithm_settings = {
            "n_steps": n_steps,
            "n_evals": n_evals,
            "simplex_size": simplex_size,
            "tol_simplex": tol_simplex,
            "pars_init_method": pars_init_method,
            "results_output_mode": results_output_mode,
        }
        if post_estimation_sections is None:
            post_estimation_sections = (SavePredictionsSection(),) if save_predictions else ()
        super().__init__(
            extra_options=extra_options,
            post_estimation_sections=post_estimation_sections,
        )

    def get_algorithm_settings(self) -> dict[str, object | None]:
        return dict(self._algorithm_settings)


class RestartingNelderMead(AlgorithmRunTemplate):
    """Programmatic template for a restarting Nelder-Mead run.m algorithm."""

    method = "nm"
    option_classes = {
        "n_steps": SetMaxStepNumberOption,
        "n_evals": SetMaxFunEvalsOption,
        "simplex_size": SetSimplexSizeOption,
        "tol_simplex": SetTolSimplexOption,
        "pars_init_method": SetParsInitMethodOption,
    }

    def __init__(
        self,
        *,
        n_steps: int | None = None,
        n_evals: int | None = None,
        simplex_size: float | None = None,
        tol_simplex: float | None = None,
        pars_init_method: int | None = None,
        n_runs: int | None = None,
        tol_restart: float | None = None,
        results_output_mode: int | None = None,
        save_predictions: bool = True,
        extra_options: tuple[EstimOption, ...] = (),
        post_estimation_sections: tuple[RunSection, ...] | None = None,
    ) -> None:
        self._algorithm_settings = {
            "n_steps": n_steps,
            "n_evals": n_evals,
            "simplex_size": simplex_size,
            "tol_simplex": tol_simplex,
            "pars_init_method": pars_init_method,
            "n_runs": n_runs,
            "tol_restart": tol_restart,
            "results_output_mode": results_output_mode,
        }
        if post_estimation_sections is None:
            post_estimation_sections = (SavePredictionsSection(),) if save_predictions else ()
        super().__init__(
            extra_options=extra_options,
            post_estimation_sections=post_estimation_sections,
        )

    def get_algorithm_settings(self) -> dict[str, object | None]:
        return dict(self._algorithm_settings)

    def get_builtin_algorithm_options(self) -> tuple[EstimOption, ...]:
        return (SetResultsOutputOption(0),)

    def build_estimation_sections(self) -> tuple[RunSection, ...]:
        settings = self.get_algorithm_settings()
        return (
            EstimationCallSection(),
            RestartLoopSection(
                n_runs=settings["n_runs"],
                tol_restart=settings["tol_restart"],
            ),
            GetResultsSection(
                results_output_mode=settings["results_output_mode"],
            ),
        )


class AlternatingRestartNelderMead(RestartingNelderMead):
    """Programmatic template for alternating restarting Nelder-Mead."""

    def build_algorithm_option(self, setting_key: str, value) -> EstimOption:
        if setting_key != "simplex_size":
            return super().build_algorithm_option(setting_key, value)
        if value is None:
            return SetSimplexSizeOption(render_key=setting_key, create_global_variable=True)
        return SetSimplexSizeOption(value, create_global_variable=True)

    def build_estimation_sections(self) -> tuple[RunSection, ...]:
        settings = self.get_algorithm_settings()
        return (
            EstimationCallSection(),
            RestartLoopSection(
                n_runs=settings["n_runs"],
                tol_restart=settings["tol_restart"],
                alternate_simplex_size=True,
            ),
            GetResultsSection(
                results_output_mode=settings["results_output_mode"],
            ),
        )
