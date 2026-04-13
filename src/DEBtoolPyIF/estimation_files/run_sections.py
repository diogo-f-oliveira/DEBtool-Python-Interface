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


