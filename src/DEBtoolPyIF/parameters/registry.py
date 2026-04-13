"""Parameter registry utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .definitions import ParameterDefinition


class ParameterRegistry:
    def __init__(self, definitions: list[ParameterDefinition] | None = None):
        self._definitions: dict[str, ParameterDefinition] = {}
        if definitions is not None:
            for definition in definitions:
                self.add(definition)

    def add(self, definition: ParameterDefinition) -> None:
        self._definitions[definition.name] = definition

    def get(self, name: str) -> ParameterDefinition | None:
        return self._definitions.get(name)

    def require(self, name: str) -> ParameterDefinition:
        definition = self.get(name)
        if definition is None:
            raise KeyError(name)
        return definition

    def copy(self) -> "ParameterRegistry":
        return ParameterRegistry(list(self._definitions.values()))

    @classmethod
    def default(cls) -> "ParameterRegistry":
        from .definitions import ParameterDefinitions

        return cls(list(ParameterDefinitions.default()))

    # TODO: Add classmethods for getting a parameter registry based on model type, e.g., stx would include also E_Hx.

    def merged(self, extra_definitions: list[ParameterDefinition] | None = None) -> "ParameterRegistry":
        merged_registry = self.copy()
        if extra_definitions:
            for definition in extra_definitions:
                merged_registry.add(definition)
        return merged_registry

    def __contains__(self, name: str) -> bool:
        return name in self._definitions


def build_default_parameter_registry() -> ParameterRegistry:
    return ParameterRegistry.default()
