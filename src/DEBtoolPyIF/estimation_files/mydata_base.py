"""Shared state and section contracts for mydata.m generation."""

from __future__ import annotations

from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, field
from typing import ClassVar

from .templates import RegisteredTemplateSection


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


class MyDataSection(RegisteredTemplateSection, ABC):
    """Render one canonical mydata substitution key."""

    template_label = "mydata"
    _registered_sections_by_family: ClassVar[dict[str, list[type["MyDataSection"]]]] = defaultdict(list)

    def render(self, context, state: BaseMyDataState) -> str:
        return self._render_matlab_code(context, state)
