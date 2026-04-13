"""Shared run.m section registry base."""

from __future__ import annotations

from abc import ABC
from collections import defaultdict
from typing import ClassVar

from .templates import RegisteredTemplateSection


class RunSection(RegisteredTemplateSection, ABC):
    """Render one canonical run.m substitution key."""

    template_label = "run"
    _registered_sections_by_family: ClassVar[dict[str, list[type["RunSection"]]]] = defaultdict(list)

    def render(self, context) -> str:
        return self._render_matlab_code(context)


class RunSetupSection(RunSection):
    key = "setup"
    template_families = ("run",)
    section_tags = ("pre_estimation",)
    matlab_code = """clear;
close all;
global pets

pets = {'${species_name}'};
check_my_pet(pets);"""

    def get_render_substitutions(self, context) -> dict[str, str]:
        return {"species_name": context.species_name}


class EstimationCallSection(RunSection):
    key = "estimation_call"
    template_families = ("run",)
    section_tags = ("estimation_call",)

    def __init__(self, set_output_args = True) -> None:
        matlab_code = "estim_pars;"
        if set_output_args:
            matlab_code = "[nsteps, converged, fval] = " + matlab_code
        super().__init__(matlab_code=matlab_code)

class SavePredictionsSection(RunSection):
    key = "save_predictions"
    template_families = ("run",)
    section_tags = ("post_estimation",)
    matlab_code = """
load(['results_' pets{1} '.mat']);
[data, auxData, metaData, txtData, weights] = feval(['mydata_' pets{1}]);
q = rmfield(par, 'free');
[prdData, info] = feval(['predict_' pets{1}], q, data, auxData); 

save(['results_' pets{1} '.mat'], 'metaData', 'metaPar', 'par', 'txtPar', 'data', 'auxData', 'txtData', 'weights', 'prdData')
"""


def _render_resolved_option_value(option, context) -> str:
    value = option.resolve_value(context)
    option.validate_value(value)
    return option.render_value(value)


def _render_positive_integer_run_value(value, *, argument_name: str, context) -> str:
    from .run_options import IntegerEstimOption

    class _PositiveIntegerRunValue(IntegerEstimOption):
        positive = True

    return _render_resolved_option_value(
        _PositiveIntegerRunValue(value, argument_name=argument_name),
        context,
    )


def _render_positive_numeric_run_value(value, *, argument_name: str, context) -> str:
    from .run_options import NumericEstimOption

    class _PositiveNumericRunValue(NumericEstimOption):
        positive = True

    return _render_resolved_option_value(
        _PositiveNumericRunValue(value, argument_name=argument_name),
        context,
    )


class RestartLoopSection(RunSection):
    key = "restart_loop"
    template_families = ("run",)
    section_tags = ("algorithm",)
    matlab_code = """n_runs = ${n_runs};
tol_restart = ${tol_restart};

estim_options('pars_init_method', 1);
estim_options('results_output', 0);
prev_fval = 1e10;
i = 2;

% Continue full-simplex runs while the objective is still improving.
while (abs(prev_fval - fval) > tol_restart) && (i <= n_runs) && ~converged
    prev_fval = fval;
    fprintf('Run %d/%d\\n', i, n_runs)
${alternate_simplex_size}
    [nsteps, converged, fval] = estim_pars;
    i = i + 1;
end"""

    def __init__(
        self,
        *,
        n_runs=None,
        tol_restart=None,
        alternate_simplex_size: bool = False,
    ) -> None:
        from .run_options import RunSetting

        if not isinstance(alternate_simplex_size, bool):
            raise TypeError(
                "RestartLoopSection alternate_simplex_size must be a bool, "
                f"not {type(alternate_simplex_size).__name__}."
            )
        self.n_runs = RunSetting("n_runs") if n_runs is None else n_runs
        self.tol_restart = RunSetting("tol_restart") if tol_restart is None else tol_restart
        self.alternate_simplex_size = alternate_simplex_size
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        return {
            "alternate_simplex_size": (
                "    simplex_size = -simplex_size;" if self.alternate_simplex_size else ""
            ),
        }

    def get_render_substitutions(self, context) -> dict[str, str]:
        return {
            "n_runs": _render_positive_integer_run_value(
                self.n_runs,
                argument_name="n_runs",
                context=context,
            ),
            "tol_restart": _render_positive_numeric_run_value(
                self.tol_restart,
                argument_name="tol_restart",
                context=context,
            ),
        }


class GetResultsSection(RunSection):
    key = "get_results"
    template_families = ("run",)
    section_tags = ("post_estimation",)
    matlab_code = """estim_options('pars_init_method', 1);
estim_options('method', 'no');
estim_options('results_output', ${results_output_mode});
estim_pars;"""

    def __init__(self, *, results_output_mode=None) -> None:
        from .run_options import RunSetting

        self.results_output_mode = (
            RunSetting("results_output_mode") if results_output_mode is None else results_output_mode
        )
        super().__init__()

    def get_render_substitutions(self, context) -> dict[str, str]:
        from .run_options import SetResultsOutputOption

        results_output_option = SetResultsOutputOption(
            self.results_output_mode,
            argument_name="results_output_mode",
        )
        return {
            "results_output_mode": _render_resolved_option_value(results_output_option, context),
        }
