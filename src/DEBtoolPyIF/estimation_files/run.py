"""run.m template families and shared section helpers."""

from __future__ import annotations

from pathlib import Path

from .run_options import (
    EstimOption,
    SetEstimOptionsSection,
    NumericEstimOption,
    RunSetting,
    SetFilterOption,
    SetMaxFunEvalsOption,
    SetMaxStepNumberOption,
    SetMethodOption,
    SetParsInitMethodOption,
    SetResultsOutputOption,
    SetSimplexSizeOption,
    SetTolSimplexOption,
    StringEstimOption,
    resolve_run_value,
)
from .run_sections import RunSection, RunSetupSection, EstimationCallSection
from .templates import ProgrammaticTemplate, SubstitutionTemplate
from ..utils.data_conversion import convert_numeric_array_to_matlab


class RunAlgorithmSection(RunSection):
    key = "algorithm"
    template_families = ("run",)
    section_tags = ("algorithm",)
    matlab_code = """[nsteps, converged, fval] = estim_pars; 

n_runs = ${n_runs};
${restart_options}
prev_fval = 1e10;
i = 2;

while (abs(prev_fval - fval) > ${tol_simplex}) && (i < n_runs) && ~converged
    prev_fval = fval;
    fprintf('Run %d\\n', i)
    [nsteps, converged, fval] = estim_pars; 
    i = i + 1;
end

${save_options}
estim_pars;
"""

    def get_render_substitutions(self, context) -> dict[str, str]:
        return {
            "n_runs": convert_numeric_array_to_matlab(resolve_run_value(RunSetting("n_runs"), context)),
            "tol_simplex": convert_numeric_array_to_matlab(resolve_run_value(RunSetting("tol_simplex"), context)),
            "restart_options": "\n".join(
                (
                    SetParsInitMethodOption(1).render(context),
                    SetResultsOutputOption(0).render(context),
                )
            ),
            "save_options": "\n".join(
                (
                    SetParsInitMethodOption(1).render(context),
                    SetResultsOutputOption(render_key="results_output_mode").render(context),
                    SetMethodOption("no").render(context),
                )
            ),
        }


class RunTemplate:
    """Shared file-family behavior for run template classes."""

    template_label = "run"
    template_families = ("run",)

    @classmethod
    def available_section_classes(cls) -> tuple[type[RunSection], ...]:
        return RunSection.registered_section_classes(
            template_families=cls.template_families,
        )

    @classmethod
    def allowed_section_keys(cls) -> tuple[str, ...]:
        registered_keys = tuple(dict.fromkeys(section_class.key for section_class in cls.available_section_classes()))
        required_keys = cls.required_section_keys()
        return required_keys + tuple(key for key in registered_keys if key not in required_keys)

    @classmethod
    def required_section_keys(cls) -> tuple[str, ...]:
        return tuple(section.key for section in cls.required_sections())

    @classmethod
    def section_classes_for_tag(cls, tag: str) -> tuple[type[RunSection], ...]:
        return RunSection.registered_section_classes(
            template_families=cls.template_families,
            tag=tag,
        )

    @classmethod
    def sections_for_tag(cls, tag: str) -> tuple[RunSection, ...]:
        return tuple(section_class() for section_class in cls.section_classes_for_tag(tag))

    @classmethod
    def required_sections(cls) -> tuple[RunSection, ...]:
        return (
            RunSetupSection(),
            SetEstimOptionsSection(),
            EstimationCallSection(),
        )

    @classmethod
    def default_sections(cls) -> tuple[RunSection, ...]:
        return cls.required_sections()

    def get_section_key(self, section) -> str:
        return section.key

    def render_section(self, section, context) -> str:
        return section.render(context)


class RunProgrammaticTemplate(RunTemplate, ProgrammaticTemplate):
    """Validated direct-assembly programmatic run template."""

    def __init__(self, *, sections: tuple[RunSection, ...] | None = None) -> None:
        final_sections = self.required_sections() if sections is None else tuple(sections)
        ProgrammaticTemplate.__init__(
            self,
            sections=final_sections,
            allowed_section_keys=self.allowed_section_keys(),
            required_section_keys=self.required_section_keys(),
            template_label=self.template_label,
        )


class RunSubstitutionTemplate(RunTemplate, SubstitutionTemplate):
    """Source-backed run template with construction-time section matching."""

    def __init__(self, *, source: str | Path, sections: tuple[RunSection, ...] | None = None) -> None:
        SubstitutionTemplate.__init__(
            self,
            source=source,
            sections=sections,
            template_label=self.template_label,
        )

    def get_default_sections(self) -> tuple:
        return self.default_sections()
