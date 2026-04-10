"""Shared state and section contracts for mydata.m generation."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from .templates import MatlabSnippetMixin


@dataclass(frozen=True)
class BaseMyDataState:
    """Shared computed state consumed by mydata section renderers."""

    entity_data_blocks: tuple[str, ...] = ()
    group_data_blocks: tuple[str, ...] = ()
    entity_data_types: tuple[str, ...] = ()
    group_data_types: tuple[str, ...] = ()
    entity_list: tuple[str, ...] = ()
    groups_of_entity: dict[str, list[str]] = field(default_factory=dict)
    extra_info: str = ""


class MyDataSection(MatlabSnippetMixin, ABC):
    """Render one canonical mydata substitution key."""

    key: str

    def __init__(self, *, matlab_code: str | None = None) -> None:
        super().__init__(matlab_code=matlab_code)

    def validate(self, allowed_keys: tuple[str, ...]) -> None:
        if self.key not in allowed_keys:
            raise ValueError(
                f"Unsupported mydata template key '{self.key}'. "
                f"Expected one of: {', '.join(allowed_keys)}."
            )

    def render(self, context, state: BaseMyDataState) -> str:
        return self._render_matlab_code(context, state)
