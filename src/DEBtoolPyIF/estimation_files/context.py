"""Generation contexts for generic estimation-file rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GenerationContext:
    """Common context shared by all estimation-file renderers."""

    species_name: str
    output_folder: Path
