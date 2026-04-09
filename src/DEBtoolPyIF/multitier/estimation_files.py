"""Multitier adapters and sections for generic estimation-file assembly."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..estimation_files.config import EstimationTemplates
from ..estimation_files.context import GenerationContext
from ..estimation_files.run import RunSubstitutionTemplate
from ..estimation_files.templates import CopyFileTemplate
from ..utils.entity_list import normalize_entity_list
from .mydata import MultitierMyDataSubstitutionTemplate
from .pars_init import MultitierParsInitSubstitutionTemplate


def build_estimation_templates_from_folder(
    template_folder: str | Path,
    tier_names: list[str] | tuple[str, ...],
    species_name: str,
) -> dict[str, EstimationTemplates]:
    template_folder = Path(template_folder)
    return {
        tier_name: EstimationTemplates(
            mydata=MultitierMyDataSubstitutionTemplate(
                source=template_folder / tier_name / f"mydata_{species_name}.m"
            ),
            pars_init=MultitierParsInitSubstitutionTemplate(
                source=template_folder / tier_name / f"pars_init_{species_name}.m"
            ),
            predict=CopyFileTemplate(template_folder / tier_name / f"predict_{species_name}.m"),
            run=RunSubstitutionTemplate(
                source=template_folder / tier_name / f"run_{species_name}.m"
            ),
        )
        for tier_name in tier_names
    }


@dataclass(frozen=True)
class MultitierGenerationContext(GenerationContext):
    """Generation context for one multitier estimation target."""

    tier_estimator: object
    tier_name: str
    entity_list: list[str]
    pseudo_data_weight: float

    @classmethod
    def from_tier_estimator(
        cls,
        tier_estimator,
        entity_list="all",
        pseudo_data_weight: float = 0.1,
        output_folder: str | Path | None = None,
    ) -> "MultitierGenerationContext":
        normalized_entity_list = normalize_entity_list(entity_list)
        if normalized_entity_list == "all":
            normalized_entity_list = list(
                tier_estimator.tier_structure.entity_hierarchy.get_entities(tier_estimator.name)
            )

        resolved_output_folder = Path(output_folder) if output_folder is not None else Path(tier_estimator.output_folder)
        return cls(
            species_name=tier_estimator.tier_structure.species_name,
            output_folder=resolved_output_folder,
            tier_estimator=tier_estimator,
            tier_name=tier_estimator.name,
            entity_list=list(normalized_entity_list),
            pseudo_data_weight=pseudo_data_weight,
        )

    @property
    def tier_structure(self):
        return self.tier_estimator.tier_structure

    @property
    def estimation_settings(self) -> dict:
        return self.tier_estimator.estimation_settings or {}

    @property
    def tier_pars(self) -> list[str]:
        return list(self.tier_estimator.tier_pars)

    @property
    def extra_info(self):
        return self.tier_estimator.extra_info

    @property
    def full_pars_dict(self) -> dict:
        return self.tier_structure.get_full_pars_dict(self.tier_name, self.entity_list[0])

    @property
    def tier_par_init_values(self) -> dict:
        return self.tier_structure.get_init_par_values(
            tier_name=self.tier_name,
            entity_list=self.entity_list,
        ).to_dict()
