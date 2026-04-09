from pathlib import Path
import warnings

import pandas as pd

from ..data_sources.collection import DataCollection
from ..estimation_files import normalize_estimation_templates
from ..estimation.runner import EstimationRunner
from .estimation_files import build_estimation_templates_from_folder
from .hierarchy import TierHierarchy
from .tier_estimation import TierEstimator


class MultiTierStructure:
    def __init__(self, species_name: str, entity_hierarchy: TierHierarchy, data: dict[str, DataCollection], pars: dict,
                 tier_pars: dict, template_folder: str | Path | None = None,
                 estimation_templates: dict | None = None,
                 output_folder: str | Path = ".", matlab_session="auto"):
        self.data = data
        self.species_name = species_name
        self.entity_hierarchy = entity_hierarchy
        self.tier_names = list(self.entity_hierarchy.tier_names)
        self.template_folder = Path(template_folder) if template_folder is not None else None
        self.output_folder = Path(output_folder)
        self.pars = pars
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

    def build_tiers(self):
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.entity_hierarchy.to_dataframe().to_csv(self.output_folder / "entity_vs_tier.csv")

        for tier_name in self.tier_names:
            tier_template_folder = self.template_folder / tier_name if self.template_folder is not None else None
            tier_pars_str = " ".join(self.tier_pars[tier_name])
            if not all([p in self.pars for p in self.tier_pars[tier_name]]):
                raise Exception(f"Cannot estimate tier pars {tier_pars_str} for {tier_name} tier as they"
                                f" are not all estimated in the previous tier.")
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

    def get_pars_from_tier_above(self, tier_name):
        return self.tiers[self.entity_hierarchy.get_parent_tier(tier_name)].pars_df

    def get_init_par_values(self, tier_name, entity_list="all"):
        if entity_list == "all":
            entity_list = list(self.entity_hierarchy.get_entities(tier_name))
        init_par_values = pd.DataFrame(columns=self.tier_pars[tier_name], index=entity_list)

        prev_tier = self.entity_hierarchy.get_parent_tier(tier_name)
        if prev_tier is None:
            for ts_id in entity_list:
                for par in self.tier_pars[tier_name]:
                    init_par_values.loc[ts_id, par] = self.pars[par]
        else:
            prev_tier_par_values = self.get_pars_from_tier_above(tier_name)
            for ts_id in entity_list:
                prev_ts_id = self.entity_hierarchy.get_entity_at_tier(tier_name, ts_id, prev_tier)
                for par in self.tier_pars[tier_name]:
                    if par in self.tiers[tier_name].pseudo_data:
                        init_par_values.loc[ts_id, par] = self.tiers[tier_name].pseudo_data.loc[ts_id, par]
                    else:
                        init_par_values.loc[ts_id, par] = prev_tier_par_values.loc[prev_ts_id, par]

        return init_par_values

    def get_full_pars_dict(self, tier_name, entity_id, include_tier=False):
        pars_dict = self.pars.copy()
        ts_tiers = self.entity_hierarchy.get_path(tier_name, entity_id)
        for current_tier_name in self.tier_names:
            if self.entity_hierarchy.get_parent_tier(current_tier_name) == tier_name:
                break
            if not include_tier and current_tier_name == tier_name:
                continue
            for par in self.tier_pars[current_tier_name]:
                pars_dict[par] = self.tiers[current_tier_name].pars_df.loc[ts_tiers[current_tier_name], par]
        return pars_dict

    def set_tier_parameters(self, tier_name, tier_pars):
        self.tier_pars[tier_name] = tier_pars
        self.tiers[tier_name].set_tier_parameters(tier_pars)
