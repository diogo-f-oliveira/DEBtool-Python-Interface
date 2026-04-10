"""run.m template families and shared section helpers."""

from __future__ import annotations

from pathlib import Path

from .templates import EstimationFileSection, ProgrammaticTemplate, SubstitutionTemplate


RUN_SLOT_NAMES = (
    "script_header",
    "setup",
    "algorithm",
    "pre_estimation_hook",
    "estimation_call",
    "post_estimation_hook",
    "pre_prediction_hook",
    "prediction_or_postprocess",
    "post_prediction_hook",
)
RUN_REQUIRED_KEYS = RUN_SLOT_NAMES
RUN_DEFAULT_SETTINGS = {
    "n_steps": 500,
    "tol_simplex": 1e-4,
    "pars_init_method": 2,
    "n_runs": 1,
    "results_output_mode": 0,
}


def get_run_settings(context) -> dict:
    settings = dict(RUN_DEFAULT_SETTINGS)
    settings.update(getattr(context, "estimation_settings", {}) or {})
    return settings


class RunScriptHeaderSection(EstimationFileSection):
    slot_name = "script_header"
    matlab_code = """% Baseline generic run template for DEBtoolPyIF.

clear;
close all;
global pets"""


class RunSetupSection(EstimationFileSection):
    slot_name = "setup"
    matlab_code = """pets = {'${species_name}'};
check_my_pet(pets);"""

    def get_render_substitutions(self, context) -> dict[str, str]:
        return {"species_name": context.species_name}


class RunAlgorithmSection(EstimationFileSection):
    slot_name = "algorithm"
    matlab_code = """estim_options('default');
estim_options('max_step_number', ${n_steps});
estim_options('max_fun_evals', 5e4);
estim_options('simplex_size', 0.05);
estim_options('filter', 0);
tol_simplex = ${tol_simplex};
estim_options('tol_simplex', tol_simplex);

estim_options('pars_init_method', ${pars_init_method});
estim_options('results_output', 0);
estim_options('method', 'nm');"""

    def get_render_substitutions(self, context) -> dict[str, str]:
        settings = get_run_settings(context)
        return {
            "n_steps": str(settings["n_steps"]),
            "tol_simplex": str(settings["tol_simplex"]),
            "pars_init_method": str(settings["pars_init_method"]),
        }


class RunEstimationCallSection(EstimationFileSection):
    slot_name = "estimation_call"
    matlab_code = """[nsteps, converged, fval] = estim_pars; %#ok<NASGU,ASGLU>

n_runs = ${n_runs};
estim_options('pars_init_method', 1);
estim_options('results_output', 0);
prev_fval = 1e10;
i = 2;

while (abs(prev_fval - fval) > tol_simplex) && (i < n_runs) && ~converged
    prev_fval = fval;
    fprintf('Run %d\\n', i)
    [nsteps, converged, fval] = estim_pars; %#ok<NASGU,ASGLU>
    i = i + 1;
end

estim_options('pars_init_method', 1);
estim_options('results_output', ${results_output_mode});
estim_options('method', 'no');
estim_pars;"""

    def get_render_substitutions(self, context) -> dict[str, str]:
        settings = get_run_settings(context)
        return {
            "n_runs": str(settings["n_runs"]),
            "results_output_mode": str(settings["results_output_mode"]),
        }


class RunPredictionSection(EstimationFileSection):
    slot_name = "prediction_or_postprocess"
    matlab_code = """load(['results_' pets{1} '.mat']);
[data, auxData, metaData, txtData, weights] = feval(['mydata_' pets{1}]);
q = rmfield(par, 'free');
[prdData, info] = feval(['predict_' pets{1}], q, data, auxData); %#ok<NASGU,ASGLU>

save(['results_' pets{1} '.mat'], 'metaData', 'metaPar', 'par', 'txtPar', 'data', 'auxData', 'txtData', 'weights', 'prdData')"""


class RunHookSection(EstimationFileSection):
    matlab_code = "${hook_code}"

    def __init__(self, *, slot_name: str, code: str = "") -> None:
        self.slot_name = slot_name
        self.code = code
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        return {"hook_code": self.code}


class RunTemplate:
    """Shared file-family behavior for run template classes."""

    template_label = "run"
    allowed_section_keys = RUN_SLOT_NAMES
    required_section_keys = RUN_REQUIRED_KEYS

    def __init__(
        self,
        *,
        pre_estimation_hook: str = "",
        post_estimation_hook: str = "",
        pre_prediction_hook: str = "",
        post_prediction_hook: str = "",
    ) -> None:
        self.pre_estimation_hook = pre_estimation_hook
        self.post_estimation_hook = post_estimation_hook
        self.pre_prediction_hook = pre_prediction_hook
        self.post_prediction_hook = post_prediction_hook

    @classmethod
    def required_sections(
        cls,
        *,
        pre_estimation_hook: str = "",
        post_estimation_hook: str = "",
        pre_prediction_hook: str = "",
        post_prediction_hook: str = "",
    ) -> tuple[EstimationFileSection, ...]:
        return (
            RunScriptHeaderSection(),
            RunSetupSection(),
            RunAlgorithmSection(),
            RunHookSection(slot_name="pre_estimation_hook", code=pre_estimation_hook),
            RunEstimationCallSection(),
            RunHookSection(slot_name="post_estimation_hook", code=post_estimation_hook),
            RunHookSection(slot_name="pre_prediction_hook", code=pre_prediction_hook),
            RunPredictionSection(),
            RunHookSection(slot_name="post_prediction_hook", code=post_prediction_hook),
        )

    @classmethod
    def default_sections(
        cls,
        *,
        pre_estimation_hook: str = "",
        post_estimation_hook: str = "",
        pre_prediction_hook: str = "",
        post_prediction_hook: str = "",
    ) -> tuple[EstimationFileSection, ...]:
        return cls.required_sections(
            pre_estimation_hook=pre_estimation_hook,
            post_estimation_hook=post_estimation_hook,
            pre_prediction_hook=pre_prediction_hook,
            post_prediction_hook=post_prediction_hook,
        )

    def get_section_key(self, section) -> str:
        return section.slot_name

    def render_section(self, section, context) -> str:
        return section.render(context)


class RunProgrammaticTemplate(RunTemplate, ProgrammaticTemplate):
    """Validated direct-assembly programmatic run template."""

    def __init__(
        self,
        *,
        pre_estimation_hook: str = "",
        post_estimation_hook: str = "",
        pre_prediction_hook: str = "",
        post_prediction_hook: str = "",
        sections: tuple[EstimationFileSection, ...] | None = None,
    ) -> None:
        RunTemplate.__init__(
            self,
            pre_estimation_hook=pre_estimation_hook,
            post_estimation_hook=post_estimation_hook,
            pre_prediction_hook=pre_prediction_hook,
            post_prediction_hook=post_prediction_hook,
        )
        final_sections = self.required_sections(
            pre_estimation_hook=self.pre_estimation_hook,
            post_estimation_hook=self.post_estimation_hook,
            pre_prediction_hook=self.pre_prediction_hook,
            post_prediction_hook=self.post_prediction_hook,
        ) if sections is None else tuple(sections)
        ProgrammaticTemplate.__init__(
            self,
            sections=final_sections,
            allowed_section_keys=self.allowed_section_keys,
            required_section_keys=self.required_section_keys,
            template_label=self.template_label,
        )


class RunSubstitutionTemplate(RunTemplate, SubstitutionTemplate):
    """Source-backed run template with construction-time section matching."""

    def __init__(
        self,
        *,
        source: str | Path,
        pre_estimation_hook: str = "",
        post_estimation_hook: str = "",
        pre_prediction_hook: str = "",
        post_prediction_hook: str = "",
        sections: tuple[EstimationFileSection, ...] | None = None,
    ) -> None:
        RunTemplate.__init__(
            self,
            pre_estimation_hook=pre_estimation_hook,
            post_estimation_hook=post_estimation_hook,
            pre_prediction_hook=pre_prediction_hook,
            post_prediction_hook=post_prediction_hook,
        )
        SubstitutionTemplate.__init__(
            self,
            source=source,
            sections=sections,
            template_label=self.template_label,
        )

    def get_default_sections(self) -> tuple:
        return self.default_sections(
            pre_estimation_hook=self.pre_estimation_hook,
            post_estimation_hook=self.post_estimation_hook,
            pre_prediction_hook=self.pre_prediction_hook,
            post_prediction_hook=self.post_prediction_hook,
        )
