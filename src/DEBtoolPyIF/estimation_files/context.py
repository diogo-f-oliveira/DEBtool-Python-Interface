"""Generation contexts for generic estimation-file rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class GenerationContext:
    """Common context shared by all estimation-file renderers."""

    species_name: str
    output_folder: Path


@dataclass(frozen=True)
class SpeciesGenerationContext(GenerationContext):
    """Generation context for a single-species (regular Add-my-Pet style) estimation.

    It provides the values that the generic ``pars_init`` and ``run`` sections read at render time:

    - ``full_pars_dict``: initial values of the model parameters rendered into ``pars_init``,
    - ``free_pars``: names of the parameters that are estimated (``free.(par) = 1``),
    - ``estimation_settings``: render-time values for ``RunSetting`` options of ``run`` templates.
    """

    full_pars_dict: dict = field(default_factory=dict)
    free_pars: tuple[str, ...] = ()
    estimation_settings: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "output_folder", Path(self.output_folder))
        object.__setattr__(self, "free_pars", tuple(self.free_pars))
        unknown_free_pars = [par for par in self.free_pars if par not in self.full_pars_dict]
        if unknown_free_pars:
            raise ValueError(
                "Free parameters must have an initial value in full_pars_dict: "
                + ", ".join(unknown_free_pars)
                + "."
            )
