"""Multitier-specific mydata state and sections."""

from __future__ import annotations

from dataclasses import dataclass, field
import warnings

from ..estimation_files.mydata_base import BaseMyDataState, MyDataSection
from ..estimation_files.mydata_packing_sections import PackingSection
from ..utils.data_conversion import convert_dict_to_matlab, convert_list_of_strings_to_matlab
from ..utils.mydata_code_generation import generate_meta_data_code, generate_tier_variable_code


@dataclass(frozen=True)
class MultitierMyDataState(BaseMyDataState):
    """Additional multitier-specific state for mydata generation."""

    tier_entities: dict[str, list[str]] = field(default_factory=dict)
    tier_groups: dict[str, list[str]] = field(default_factory=dict)
    tier_subtree: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    tier_pars: tuple[str, ...] = ()
    tier_par_init_values: dict[str, dict] = field(default_factory=dict)


def _sorted_unique_strings(values):
    return sorted(set(values))


def build_multitier_mydata_state(context) -> MultitierMyDataState:
    entity_data_blocks = []
    group_data_blocks = []
    entity_data_types = set()
    group_data_types = set()
    entity_list = tuple(context.entity_list)
    groups_of_entity = {}
    tier_entities = {}
    tier_groups = {}
    tier_subtree = {entity_id: {} for entity_id in context.entity_list}

    for tier_name in context.tier_structure.entity_hierarchy.get_all_tiers_below(context.tier_name):
        tier = context.tier_structure.tiers[tier_name]

        tier_entities_to_include = set()
        tier_groups_to_include = set()
        for entity_id in context.entity_list:
            mapped_entities = context.tier_structure.entity_hierarchy.map_entities(
                source_tier=context.tier_name,
                target_tier=tier_name,
                entity_list=[entity_id],
            )
            tier_entities_to_include.update(mapped_entities)
            get_group_list = getattr(tier.data, "get_group_list_from_entity_list", None)
            if callable(get_group_list):
                tier_groups_to_include.update(get_group_list(mapped_entities))

            if tier_name != context.tier_name:
                tier_subtree[entity_id][tier_name] = list(mapped_entities)

        get_entity_code = getattr(tier.data, "get_entity_mydata_code", None)
        if callable(get_entity_code):
            entity_types, entity_blocks = get_entity_code(tier_entities_to_include)
        else:
            entity_types, entity_blocks = list(getattr(tier.data, "entity_data_types", [])), []
        entity_data_types.update(entity_types)
        entity_data_blocks.extend(entity_blocks)

        get_group_code = getattr(tier.data, "get_group_mydata_code", None)
        if callable(get_group_code):
            group_types, group_blocks = get_group_code(tier_entities_to_include)
        else:
            group_types, group_blocks = list(getattr(tier.data, "group_data_types", [])), []
        group_data_types.update(group_types)
        group_data_blocks.extend(group_blocks)

        tier_entities[tier_name] = list(tier_entities_to_include)
        tier_groups[tier_name] = list(tier_groups_to_include)
        get_groups_of_entities = getattr(tier.data, "get_groups_of_entities", None)
        if callable(get_groups_of_entities):
            groups_of_entity.update(get_groups_of_entities(tier_entities_to_include))
        else:
            groups_of_entity.update({entity_id: [] for entity_id in tier_entities_to_include})

    return MultitierMyDataState(
        entity_data_blocks=tuple(entity_data_blocks),
        group_data_blocks=tuple(group_data_blocks),
        entity_data_types=tuple(_sorted_unique_strings(entity_data_types)),
        group_data_types=tuple(_sorted_unique_strings(group_data_types)),
        entity_list=entity_list,
        groups_of_entity=groups_of_entity,
        extra_info=context.extra_info,
        tier_entities=tier_entities,
        tier_groups=tier_groups,
        tier_subtree=tier_subtree,
        tier_pars=tuple(context.tier_pars),
        tier_par_init_values=context.tier_par_init_values,
    )


class TierEntitiesSection(MyDataSection):
    key = "tier_entities"

    def render(self, _context, state: MultitierMyDataState) -> str:
        return generate_tier_variable_code(
            var_name="tier_entities",
            converted_data=convert_dict_to_matlab(
                {
                    tier_name: convert_list_of_strings_to_matlab(entity_ids, double_brackets=True)
                    for tier_name, entity_ids in state.tier_entities.items()
                }
            ),
            label="List of entity ids for each tier",
        )


class TierGroupsSection(MyDataSection):
    key = "tier_groups"

    def render(self, _context, state: MultitierMyDataState) -> str:
        return generate_tier_variable_code(
            var_name="tier_groups",
            converted_data=convert_dict_to_matlab(
                {
                    tier_name: convert_list_of_strings_to_matlab(group_ids, double_brackets=True)
                    for tier_name, group_ids in state.tier_groups.items()
                }
            ),
            label="List of groups ids for each tier",
        )


class TierSubtreeSection(MyDataSection):
    key = "tier_subtree"

    def render(self, _context, state: MultitierMyDataState) -> str:
        return generate_tier_variable_code(
            var_name="tier_subtree",
            converted_data=convert_dict_to_matlab(
                {
                    entity_id: convert_dict_to_matlab(
                        {
                            tier_name: convert_list_of_strings_to_matlab(entity_ids, double_brackets=True)
                            for tier_name, entity_ids in subtree.items()
                        }
                    )
                    for entity_id, subtree in state.tier_subtree.items()
                }
            ),
            label="Tier subtree",
        )


class TierParsSection(MyDataSection):
    key = "tier_pars"

    def render(self, _context, state: MultitierMyDataState) -> str:
        return generate_tier_variable_code(
            var_name="tier_pars",
            converted_data=convert_list_of_strings_to_matlab(list(state.tier_pars)),
            label="Tier parameters",
            comment="Tier parameters",
            pars_init_access=True,
        )


class TierParInitValuesSection(MyDataSection):
    key = "tier_par_init_values"

    def render(self, _context, state: MultitierMyDataState) -> str:
        return generate_meta_data_code(
            var_name="tier_par_init_values",
            converted_data=convert_dict_to_matlab(
                {
                    parameter_name: convert_dict_to_matlab(initial_values)
                    for parameter_name, initial_values in state.tier_par_init_values.items()
                }
            ),
        )


class MultitierPseudoDataSection(MyDataSection):
    key = "multitier_pseudodata_block"
    matlab_code = """%% Add multitier pseudo-data from previous-tier estimates
for e = 1:length(tiers.entity_list)
    entity_id = tiers.entity_list{e};
    for p = 1:length(tiers.tier_pars)
        par_name = tiers.tier_pars{p};
        varname = [par_name '_' entity_id];

        data.psd.(varname) = metaData.tier_par_init_values.(par_name).(entity_id);
        units.psd.(varname) = '';
        label.psd.(varname) = '';
        weights.psd.(varname) = ${pseudo_data_weight};
    end
end"""

    def render(self, context, _state: MultitierMyDataState) -> str:
        if context.tier_structure.entity_hierarchy.get_parent_tier(context.tier_name) is None:
            return ""
        return super().render(context, _state)

    def get_render_substitutions(self, context, state: MultitierMyDataState | None = None) -> dict[str, str]:
        substitutions = super().get_render_substitutions(context, state)
        substitutions["pseudo_data_weight"] = str(context.pseudo_data_weight)
        return substitutions


class MultitierPackingSection(PackingSection):
    def __init__(
        self,
        *,
        aux_data_fields: list[str] | tuple[str, ...] = ("temp", "tiers", "init"),
        txt_data_fields: list[str] | tuple[str, ...] = ("units", "label", "bibkey", "comment", "title"),
    ) -> None:
        if "tiers" not in aux_data_fields:
            warnings.warn(
                "MultitierPackingSection was initialized without 'tiers' in aux_data_fields; "
                "pars_init.m and predict.m files may not have access to tier structure data.",
                stacklevel=2,
            )

        super().__init__(
            aux_data_fields=aux_data_fields,
            txt_data_fields=txt_data_fields,
        )
