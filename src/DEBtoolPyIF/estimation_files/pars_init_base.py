"""Shared section contract for pars_init.m generation."""

from __future__ import annotations

from abc import ABC
from collections import defaultdict
from typing import ClassVar

from .templates import RegisteredTemplateSection


class ParsInitSection(RegisteredTemplateSection, ABC):
    """Render one canonical pars_init.m substitution key."""

    template_label = "pars_init"
    _registered_sections_by_family: ClassVar[dict[str, list[type["ParsInitSection"]]]] = defaultdict(list)

    def render(self, context) -> str:
        return self._render_matlab_code(context)
