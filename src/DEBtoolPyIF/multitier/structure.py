from pathlib import Path
import warnings

from ..data_sources.collection import DataCollection
from ..estimation_files import normalize_estimation_templates
from ..estimation.runner import EstimationRunner
from .estimation_files import build_estimation_templates_from_folder
from .hierarchy import TierHierarchy
from .tier_estimation import TierEstimator


class MultiTierStructure:
    def __init__(self, species_name: str, entity_hierarchy: TierHierarchy,
                 data: dict[str, DataCollection], pars: dict | None = None,
                 tier_pars: dict | None = None, template_folder: str | Path | None = None,
                 estimation_templates: dict | None = None,
                 output_folder: str | Path = ".", matlab_session="auto",
                 *, base_pars: dict | None = None):
        self.data = data
        self.species_name = species_name
        self.entity_hierarchy = entity_hierarchy
        self.template_folder = Path(template_folder) if template_folder is not None else None
        self.output_folder = Path(output_folder)
        if pars is not None and base_pars is not None:
            raise ValueError("Pass either base_pars or deprecated pars, not both.")
        if pars is not None:
            warnings.warn(
                "MultiTierStructure(..., pars=...) is deprecated. "
                "Pass root-tier initial values to TierEstimator.estimate(initial_pars=...) instead, "
                "or use base_pars as a compatibility fallback.",
                DeprecationWarning,
                stacklevel=2,
            )
        if tier_pars is None:
            raise ValueError("tier_pars must be provided.")
        self.base_pars = dict(base_pars if base_pars is not None else (pars or {}))
        self.pars = self.base_pars
        self.tier_pars = tier_pars
        if estimation_templates is None:
            if self.template_folder is None:
                raise ValueError("Either estimation_templates or template_folder must be provided.")
            warnings.warn(
                "template_folder is deprecated and will be removed in 0.4.0. "
                "Pass estimation_templates instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.estimation_templates = build_estimation_templates_from_folder(
                template_folder=self.template_folder,
                tier_names=self.tier_names,
                species_name=self.species_name,
            )
        else:
            self.estimation_templates = normalize_estimation_templates(
                estimation_templates=estimation_templates,
                tier_names=self.tier_names,
            )
        self.tiers = {}
        self.build_tiers()
        self.estimation_runner = EstimationRunner(
            estim_files_dir=self.output_folder,
            species_name=self.species_name,
            matlab_session=matlab_session,
        )

    @property
    def tier_names(self):
        return list(self.entity_hierarchy.tier_names)

    def build_tiers(self):
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.entity_hierarchy.to_dataframe().to_csv(self.output_folder / "entity_vs_tier.csv")

        for tier_name in self.tier_names:
            tier_template_folder = self.template_folder / tier_name if self.template_folder is not None else None
            tier_output_folder = self.output_folder / tier_name

            tier_output_folder.mkdir(parents=True, exist_ok=True)
            self.tiers[tier_name] = TierEstimator(
                tier_structure=self,
                tier_name=tier_name,
                tier_pars=self.tier_pars[tier_name],
                template_folder=tier_template_folder,
                estimation_templates=self.estimation_templates[tier_name],
                output_folder=tier_output_folder,
            )

        assert self.tier_names == list(self.tiers.keys())

    def get_pars_from_tier_above(self, tier_name):
        return self.tiers[self.entity_hierarchy.get_parent_tier(tier_name)].pars_df

    def get_init_par_values(self, tier_name, entity_list="all"):
        return self.tiers[tier_name].get_initial_parameter_values(entity_list=entity_list)

    def get_full_pars_dict(self, tier_name, entity_id, include_tier=False):
        pars_dict = self.base_pars.copy()
        ts_tiers = self.entity_hierarchy.get_path(tier_name, entity_id)
        for current_tier_name in self.tier_names:
            if self.entity_hierarchy.get_parent_tier(current_tier_name) == tier_name:
                break
            current_tier = self.tiers[current_tier_name]
            current_entity_id = ts_tiers[current_tier_name]
            if current_tier_name == tier_name and not include_tier:
                current_initial_values = current_tier.get_initial_parameter_values(entity_list=[current_entity_id])
                for par in self.tier_pars[current_tier_name]:
                    pars_dict[par] = current_initial_values.loc[current_entity_id, par]
                continue
            for par in self.tier_pars[current_tier_name]:
                pars_dict[par] = current_tier.pars_df.loc[current_entity_id, par]
        return pars_dict

    def set_tier_parameters(self, tier_name, tier_pars):
        self.tier_pars[tier_name] = tier_pars
        self.tiers[tier_name].set_tier_parameters(tier_pars)
