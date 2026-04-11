"""Shared state and section contracts for mydata.m generation."""

from __future__ import annotations

from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, field
from typing import ClassVar

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
    template_families: tuple[str, ...] = ()
    section_tags: tuple[str, ...] = ()
    _registered_sections_by_family: ClassVar[dict[str, list[type["MyDataSection"]]]] = defaultdict(list)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        template_families = tuple(cls.__dict__.get("template_families", ()))
        if not template_families:
            return

        key = getattr(cls, "key", "")
        if not isinstance(key, str) or not key:
            raise ValueError(
                f"{cls.__name__} must define a non-empty 'key' to register as a mydata section."
            )

        for family in template_families:
            registered_sections = cls._registered_sections_by_family[family]
            duplicate_section = next(
                (section for section in registered_sections if section.key == key and section is not cls),
                None,
            )
            if duplicate_section is not None:
                raise ValueError(
                    f"Duplicate mydata section key '{key}' for template family '{family}': "
                    f"{duplicate_section.__name__} and {cls.__name__}."
                )
            if cls not in registered_sections:
                registered_sections.append(cls)

    @classmethod
    def registered_section_classes(
        cls,
        *,
        template_families: str | tuple[str, ...],
        tag: str | None = None,
    ) -> tuple[type["MyDataSection"], ...]:
        if isinstance(template_families, str):
            template_families = (template_families,)

        registered_sections = []
        seen_sections = set()
        key_indices: dict[str, int] = {}
        for family in template_families:
            for section in cls._registered_sections_by_family.get(family, ()):
                if section in seen_sections:
                    continue

                seen_sections.add(section)
                existing_index = key_indices.get(section.key)
                if existing_index is None:
                    key_indices[section.key] = len(registered_sections)
                    registered_sections.append(section)
                else:
                    registered_sections[existing_index] = section

        if tag is None:
            return tuple(registered_sections)
        return tuple(section for section in registered_sections if tag in section.section_tags)

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
