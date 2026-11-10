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

    def merged(self, extra_definitions: list[ParameterDefinition] | None = None) -> "ParameterRegistry":
        merged_registry = self.copy()
        if extra_definitions:
            for definition in extra_definitions:
                merged_registry.add(definition)
        return merged_registry

    def __contains__(self, name: str) -> bool:
        return name in self._definitions


class StdParameterRegistry(ParameterRegistry):
    def __init__(self) -> None:
        from .definitions import DEFAULT_PARAMETER_DEFINITIONS

        super().__init__(list(DEFAULT_PARAMETER_DEFINITIONS))


class StxParameterRegistry(StdParameterRegistry):
    def __init__(self) -> None:
        from .definitions import E_Hx, t_0

        super().__init__()
        self.add(E_Hx)
        self.add(t_0)


def get_parameter_registry_of_typified_model(model: str) -> ParameterRegistry:
    if model == "std":
        return StdParameterRegistry()
    if model == "stx":
        return StxParameterRegistry()
    if model == "nat":
        raise ValueError(
            "No built-in parameter registry is available for model 'nat'. "
            "Provide a custom ParameterRegistry explicitly."
        )
    raise ValueError(
        f"No built-in parameter registry is available for model '{model}'. "
        "Built-in registries are only available for 'std' and 'stx'."
    )
