from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union

import pandas as pd

from ..utils.mydata_code_generation import (
    is_valid_matlab_field_name,
    sanitize_matlab_field_name,
)


class TierHierarchyError(ValueError):
    """Raised when a hierarchy definition is invalid."""


class TierHierarchy:
    """
    Ordered tree of entities across named tiers.

    The simplest way to define a hierarchy is either:

    1. Directly, with entities per tier and a parent mapping for each non-root tier.
    2. From contiguous root-to-entity paths via ``from_paths(...)``.

    Example
    -------
    >>> hierarchy = TierHierarchy(
    ...     tier_names=["breed", "diet", "individual"],
    ...     entities={
    ...         "breed": ["male"],
    ...         "diet": ["CTRL", "TMR"],
    ...         "individual": ["PT1", "PT2", "PT3"],
    ...     },
    ...     parents={
    ...         "diet": {"CTRL": "male", "TMR": "male"},
    ...         "individual": {"PT1": "CTRL", "PT2": "CTRL", "PT3": "TMR"},
    ...     },
    ... )

    Paths do not need to reach the deepest tier. For example, if an entity exists in the
    root tier but has no descendants, a one-element path like ``{"sex": "female"}`` is valid.
    """

    def __init__(
            self,
            tier_names: Sequence[str],
            entities: Mapping[str, Sequence[str]],
            parents: Optional[Mapping[str, Mapping[str, str]]] = None,
    ) -> None:
        self.tier_names = self._normalize_tier_names(tier_names)
        self.entities = self._normalize_entities(self.tier_names, entities)
        self.parents = self._normalize_parents(self.tier_names, self.entities, parents or {})
        (
            self.matlab_entities,
            self.entity_to_matlab_id,
            self.matlab_id_to_entity,
        ) = self._build_matlab_entity_maps()
        self._children = self._build_children_index()

    @classmethod
    def from_paths(
            cls,
            tier_names: Sequence[str],
            paths: Sequence[Mapping[str, str]],
    ) -> "TierHierarchy":
        normalized_tier_names = cls._normalize_tier_names(tier_names)
        if not paths:
            raise TierHierarchyError("Expected at least one path.")

        entities: Dict[str, List[str]] = {tier_name: [] for tier_name in normalized_tier_names}
        parents: Dict[str, Dict[str, str]] = {
            tier_name: {} for tier_name in normalized_tier_names[1:]
        }

        for path in paths:
            extra_tiers = [tier_name for tier_name in path if tier_name not in normalized_tier_names]
            if extra_tiers:
                raise TierHierarchyError(
                    "Paths cannot reference unknown tiers. "
                    f"Extra: {extra_tiers}."
                )

            path_values = cls._extract_path_from_mapping(path, normalized_tier_names, context="Path")

            for index, tier_name in enumerate(path_values):
                entity_id = path_values[tier_name]
                if entity_id not in entities[tier_name]:
                    entities[tier_name].append(entity_id)

                if index == 0:
                    continue

                parent_tier = normalized_tier_names[index - 1]
                parent_id = path_values[parent_tier]
                registered_parent = parents[tier_name].get(entity_id)
                if registered_parent is not None and registered_parent != parent_id:
                    raise TierHierarchyError(
                        f"Entity '{entity_id}' in tier '{tier_name}' has inconsistent parents: "
                        f"'{registered_parent}' and '{parent_id}'."
                    )
                parents[tier_name][entity_id] = parent_id

        return cls(tier_names=normalized_tier_names, entities=entities, parents=parents)

    @classmethod
    def from_dataframe(cls, dataframe: pd.DataFrame) -> "TierHierarchy":
        if dataframe.empty:
            raise TierHierarchyError("Expected at least one hierarchy row in dataframe.")

        working_dataframe = dataframe.copy()
        if isinstance(working_dataframe.index, pd.MultiIndex):
            working_dataframe = working_dataframe.reset_index()

        if "tier" not in working_dataframe.columns or "entity" not in working_dataframe.columns:
            raise TierHierarchyError(
                "Hierarchy dataframe must expose 'tier' and 'entity' either as columns or as index levels."
            )

        tier_names = [column for column in working_dataframe.columns if column not in {"tier", "entity"}]
        if not tier_names:
            raise TierHierarchyError("Hierarchy dataframe must include at least one tier column.")

        entities: Dict[str, List[str]] = {tier_name: [] for tier_name in tier_names}
        parents: Dict[str, Dict[str, str]] = {tier_name: {} for tier_name in tier_names[1:]}

        for row_number, row in enumerate(working_dataframe.to_dict(orient="records"), start=1):
            row_tier = row["tier"]
            row_entity = row["entity"]
            if row_tier not in tier_names:
                raise TierHierarchyError(
                    f"Row {row_number} references unknown tier '{row_tier}'. Expected one of {tier_names}."
                )

            path = cls._extract_dataframe_path(
                row=row,
                row_number=row_number,
                tier_names=tier_names,
            )

            deepest_tier = list(path.keys())[-1]
            deepest_entity = path[deepest_tier]
            if row_tier != deepest_tier:
                raise TierHierarchyError(
                    f"Row {row_number} declares tier '{row_tier}', but the deepest populated tier is "
                    f"'{deepest_tier}'."
                )
            if row_entity != deepest_entity:
                raise TierHierarchyError(
                    f"Row {row_number} declares entity '{row_entity}', but the value in column '{row_tier}' is "
                    f"'{deepest_entity}'."
                )

            for tier_name, entity_id in path.items():
                if entity_id not in entities[tier_name]:
                    entities[tier_name].append(entity_id)

            for tier_index in range(1, len(path)):
                tier_name = tier_names[tier_index]
                child_id = path[tier_name]
                parent_id = path[tier_names[tier_index - 1]]
                existing_parent = parents[tier_name].get(child_id)
                if existing_parent is not None and existing_parent != parent_id:
                    raise TierHierarchyError(
                        f"Entity '{child_id}' in tier '{tier_name}' has inconsistent parents: "
                        f"'{existing_parent}' and '{parent_id}'."
                    )
                parents[tier_name][child_id] = parent_id

        return cls(tier_names=tier_names, entities=entities, parents=parents)

    @property
    def root_tier(self) -> str:
        return self.tier_names[0]

    def get_entities(self, tier_name: str) -> Tuple[str, ...]:
        self._require_known_tier(tier_name)
        return self.entities[tier_name]

    def get_matlab_entities(self, tier_name: str) -> Tuple[str, ...]:
        self._require_known_tier(tier_name)
        return self.matlab_entities[tier_name]

    def get_parent(self, tier_name: str, entity_id: str) -> Optional[str]:
        self._require_known_entity(tier_name, entity_id)
        if tier_name == self.root_tier:
            return None
        return self.parents[tier_name][entity_id]

    def get_matlab_entity_id(self, tier_name: str, entity_id: str) -> str:
        self._require_known_entity(tier_name, entity_id)
        return self.entity_to_matlab_id[tier_name][entity_id]

    def get_entity_at_tier(self, tier_name: str, entity_id: str, target_tier: str) -> str:
        self._require_known_entity(tier_name, entity_id)
        self._require_known_tier(target_tier)
        if self.get_tier_index(target_tier) > self.get_tier_index(tier_name):
            raise TierHierarchyError(
                f"Tier '{target_tier}' is below '{tier_name}', so '{entity_id}' has no single ancestor there."
            )
        return self.get_path(tier_name, entity_id)[target_tier]

    def get_children(self, tier_name: str, entity_id: str) -> Tuple[str, ...]:
        self._require_known_entity(tier_name, entity_id)
        child_tier = self.get_child_tier(tier_name)
        if child_tier is None:
            return tuple()
        return self._children[tier_name][entity_id]

    def get_path(self, tier_name: str, entity_id: str) -> Dict[str, str]:
        self._require_known_entity(tier_name, entity_id)
        tier_index = self.get_tier_index(tier_name)
        path: Dict[str, str] = {}
        current_tier = tier_name
        current_entity = entity_id

        for _ in range(tier_index, -1, -1):
            path[current_tier] = current_entity
            parent_tier = self.get_parent_tier(current_tier)
            if parent_tier is None:
                break
            current_entity = self.parents[current_tier][current_entity]
            current_tier = parent_tier

        return {tier: path[tier] for tier in self.tier_names[: tier_index + 1]}

    def get_descendants(
            self,
            tier_name: str,
            entity_id: str,
            descendant_tier: str,
    ) -> Tuple[str, ...]:
        self._require_known_entity(tier_name, entity_id)
        self._require_known_tier(descendant_tier)
        if self.get_tier_index(descendant_tier) < self.get_tier_index(tier_name):
            raise TierHierarchyError(
                f"Tier '{descendant_tier}' is above '{tier_name}', so it cannot contain descendants."
            )

        current_entities = [entity_id]
        current_tier = tier_name
        while current_tier != descendant_tier:
            child_tier = self.get_child_tier(current_tier)
            next_entities: List[str] = []
            for current_entity in current_entities:
                next_entities.extend(self._children[current_tier][current_entity])
            current_entities = next_entities
            current_tier = child_tier  # type: ignore[assignment]

        return tuple(current_entities)

    def get_tier_index(self, tier_name: str) -> int:
        self._require_known_tier(tier_name)
        return self.tier_names.index(tier_name)

    def is_tier_below(self, tier_name: str, other_tier: str) -> bool:
        return self.get_tier_index(tier_name) < self.get_tier_index(other_tier)

    def get_all_tiers_below(self, tier_name: str) -> Tuple[str, ...]:
        tier_index = self.get_tier_index(tier_name)
        return self.tier_names[tier_index:]

    def get_parent_tier(self, tier_name: str) -> Optional[str]:
        tier_index = self.get_tier_index(tier_name)
        if tier_index == 0:
            return None
        return self.tier_names[tier_index - 1]

    def get_child_tier(self, tier_name: str) -> Optional[str]:
        tier_index = self.get_tier_index(tier_name)
        if tier_index == len(self.tier_names) - 1:
            return None
        return self.tier_names[tier_index + 1]

    def to_records(self) -> List[Dict[str, Optional[str]]]:
        records: List[Dict[str, Optional[str]]] = []
        for tier_name in self.tier_names:
            for entity_id in self.entities[tier_name]:
                path = self.get_path(tier_name, entity_id)
                record: Dict[str, Optional[str]] = {"tier": tier_name, "entity": entity_id}
                for output_tier in self.tier_names:
                    record[output_tier] = path.get(output_tier)
                records.append(record)
        return records

    def to_dataframe(self) -> pd.DataFrame:
        dataframe = pd.DataFrame.from_records(self.to_records())
        dataframe.set_index(["tier", "entity"], inplace=True)
        return dataframe[list(self.tier_names)]

    def map_entities(
            self,
            source_tier: str,
            target_tier: str,
            entity_list: Union[Sequence[str], str] = "all",
    ) -> Tuple[str, ...]:
        self._require_known_tier(source_tier)
        self._require_known_tier(target_tier)

        if entity_list == "all":
            normalized_entities = list(self.get_entities(source_tier))
        elif isinstance(entity_list, str):
            normalized_entities = [self._validate_entity_id(entity_list, tier_name=source_tier)]
            self._require_known_entity(source_tier, normalized_entities[0])
        else:
            normalized_entities = [self._validate_entity_id(entity_id, tier_name=source_tier) for entity_id in entity_list]
            for entity_id in normalized_entities:
                self._require_known_entity(source_tier, entity_id)

        if source_tier == target_tier:
            return tuple(normalized_entities)

        source_index = self.get_tier_index(source_tier)
        target_index = self.get_tier_index(target_tier)

        if target_index < source_index:
            ordered_entities: List[str] = []
            for entity_id in normalized_entities:
                mapped_entity = self.get_entity_at_tier(source_tier, entity_id, target_tier)
                if mapped_entity not in ordered_entities:
                    ordered_entities.append(mapped_entity)
            return tuple(ordered_entities)

        source_entities = set(normalized_entities)
        ordered_descendants: List[str] = []
        for entity_id in self.get_entities(target_tier):
            if self.get_entity_at_tier(target_tier, entity_id, source_tier) in source_entities:
                ordered_descendants.append(entity_id)
        return tuple(ordered_descendants)

    def _build_children_index(self) -> Dict[str, Dict[str, Tuple[str, ...]]]:
        children_index: Dict[str, Dict[str, Tuple[str, ...]]] = {
            tier_name: {entity_id: tuple() for entity_id in entity_ids}
            for tier_name, entity_ids in self.entities.items()
        }

        for tier_name in self.tier_names[1:]:
            parent_tier = self.get_parent_tier(tier_name)
            parent_to_children: Dict[str, List[str]] = {
                parent_id: [] for parent_id in self.entities[parent_tier]  # type: ignore[index]
            }
            for child_id in self.entities[tier_name]:
                parent_id = self.parents[tier_name][child_id]
                parent_to_children[parent_id].append(child_id)

            children_index[parent_tier] = {  # type: ignore[index]
                parent_id: tuple(child_ids)
                for parent_id, child_ids in parent_to_children.items()
            }

        return children_index

    def _build_matlab_entity_maps(
            self,
    ) -> Tuple[Dict[str, Tuple[str, ...]], Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:
        matlab_entities: Dict[str, Tuple[str, ...]] = {}
        entity_to_matlab_id: Dict[str, Dict[str, str]] = {}
        matlab_id_to_entity: Dict[str, Dict[str, str]] = {}

        for tier_name, entity_ids in self.entities.items():
            tier_entity_to_matlab: Dict[str, str] = {}
            tier_matlab_to_entity: Dict[str, str] = {}
            tier_matlab_entities: List[str] = []

            for entity_id in entity_ids:
                matlab_id = sanitize_matlab_field_name(entity_id)
                if not is_valid_matlab_field_name(matlab_id):
                    raise TierHierarchyError(
                        f"Entity '{entity_id}' in tier '{tier_name}' could not be converted into a valid MATLAB "
                        f"field name."
                    )

                existing_entity = tier_matlab_to_entity.get(matlab_id)
                if existing_entity is not None and existing_entity != entity_id:
                    raise TierHierarchyError(
                        f"Entities '{existing_entity}' and '{entity_id}' in tier '{tier_name}' sanitize to the "
                        f"same MATLAB field name '{matlab_id}'."
                    )

                tier_entity_to_matlab[entity_id] = matlab_id
                tier_matlab_to_entity[matlab_id] = entity_id
                tier_matlab_entities.append(matlab_id)

            matlab_entities[tier_name] = tuple(tier_matlab_entities)
            entity_to_matlab_id[tier_name] = tier_entity_to_matlab
            matlab_id_to_entity[tier_name] = tier_matlab_to_entity

        return matlab_entities, entity_to_matlab_id, matlab_id_to_entity

    @staticmethod
    def _normalize_tier_names(tier_names: Sequence[str]) -> Tuple[str, ...]:
        normalized = tuple(tier_names)
        if not normalized:
            raise TierHierarchyError("Expected at least one tier.")
        if any(not isinstance(tier_name, str) or not tier_name.strip() for tier_name in normalized):
            raise TierHierarchyError("Tier names must be non-empty strings.")
        if len(set(normalized)) != len(normalized):
            raise TierHierarchyError("Tier names must be unique.")
        return normalized

    @classmethod
    def _normalize_entities(
            cls,
            tier_names: Tuple[str, ...],
            entities: Mapping[str, Sequence[str]],
    ) -> Dict[str, Tuple[str, ...]]:
        missing_tiers = [tier_name for tier_name in tier_names if tier_name not in entities]
        extra_tiers = [tier_name for tier_name in entities if tier_name not in tier_names]
        if missing_tiers or extra_tiers:
            raise TierHierarchyError(
                "Entities must be defined for exactly the declared tiers. "
                f"Missing: {missing_tiers or 'none'}; extra: {extra_tiers or 'none'}."
            )

        normalized: Dict[str, Tuple[str, ...]] = {}
        for tier_name in tier_names:
            entity_ids = tuple(
                cls._validate_entity_id(entity_id, tier_name=tier_name)
                for entity_id in entities[tier_name]
            )
            if not entity_ids:
                raise TierHierarchyError(f"Tier '{tier_name}' must contain at least one entity.")
            if len(set(entity_ids)) != len(entity_ids):
                raise TierHierarchyError(f"Tier '{tier_name}' contains duplicate entity identifiers.")
            normalized[tier_name] = entity_ids
        return normalized

    @classmethod
    def _normalize_parents(
            cls,
            tier_names: Tuple[str, ...],
            entities: Mapping[str, Tuple[str, ...]],
            parents: Mapping[str, Mapping[str, str]],
    ) -> Dict[str, Dict[str, str]]:
        root_tier = tier_names[0]
        if root_tier in parents and parents[root_tier]:
            raise TierHierarchyError(f"Root tier '{root_tier}' cannot define parent mappings.")

        normalized: Dict[str, Dict[str, str]] = {}
        for tier_index, tier_name in enumerate(tier_names):
            if tier_index == 0:
                continue

            if tier_name not in parents:
                raise TierHierarchyError(f"Missing parent mapping for tier '{tier_name}'.")

            parent_tier = tier_names[tier_index - 1]
            parent_mapping = parents[tier_name]
            child_ids = set(entities[tier_name])
            missing_entities = [entity_id for entity_id in entities[tier_name] if entity_id not in parent_mapping]
            extra_entities = [entity_id for entity_id in parent_mapping if entity_id not in child_ids]
            if missing_entities or extra_entities:
                raise TierHierarchyError(
                    f"Parent mapping for tier '{tier_name}' must match its entities exactly. "
                    f"Missing: {missing_entities or 'none'}; extra: {extra_entities or 'none'}."
                )

            normalized[tier_name] = {}
            valid_parents = set(entities[parent_tier])
            for child_id in entities[tier_name]:
                parent_id = cls._validate_entity_id(parent_mapping[child_id], tier_name=parent_tier)
                if parent_id not in valid_parents:
                    raise TierHierarchyError(
                        f"Parent '{parent_id}' of entity '{child_id}' in tier '{tier_name}' "
                        f"does not exist in tier '{parent_tier}'."
                    )
                normalized[tier_name][child_id] = parent_id

        unknown_tiers = [tier_name for tier_name in parents if tier_name not in tier_names]
        if unknown_tiers:
            raise TierHierarchyError(f"Parent mappings provided for unknown tiers: {unknown_tiers}.")

        return normalized

    @staticmethod
    def _validate_entity_id(entity_id: str, tier_name: str) -> str:
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise TierHierarchyError(
                f"Entity identifiers in tier '{tier_name}' must be non-empty strings."
            )
        return entity_id.strip()

    @classmethod
    def _extract_dataframe_path(
            cls,
            row: Mapping[str, object],
            row_number: int,
            tier_names: Sequence[str],
    ) -> Dict[str, str]:
        extracted_row = {
            tier_name: row.get(tier_name)
            for tier_name in tier_names
        }
        return cls._extract_path_from_mapping(
            extracted_row,
            tier_names,
            context=f"Row {row_number}",
        )

    @classmethod
    def _extract_path_from_mapping(
            cls,
            values: Mapping[str, object],
            tier_names: Sequence[str],
            context: str,
    ) -> Dict[str, str]:
        path: Dict[str, str] = {}
        seen_null = False

        for tier_name in tier_names:
            value = values.get(tier_name)
            if pd.isna(value):
                seen_null = True
                continue

            if seen_null:
                raise TierHierarchyError(
                    f"{context} contains a non-null value in tier '{tier_name}' after an empty tier column. "
                    "Paths must define a contiguous root-to-entity lineage."
                )

            path[tier_name] = cls._validate_entity_id(value, tier_name=tier_name)

        if not path:
            raise TierHierarchyError(f"{context} does not define any hierarchy path.")

        return path

    def _require_known_tier(self, tier_name: str) -> None:
        if tier_name not in self.tier_names:
            raise TierHierarchyError(f"Unknown tier '{tier_name}'.")

    def _require_known_entity(self, tier_name: str, entity_id: str) -> None:
        self._require_known_tier(tier_name)
        if entity_id not in self.entities[tier_name]:
            raise TierHierarchyError(f"Unknown entity '{entity_id}' in tier '{tier_name}'.")
