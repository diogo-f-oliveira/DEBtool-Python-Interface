"""Chemical parameter helpers for pars_init generation."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from .definitions import ParameterDefinition


def _normalize_compound_token(compound: str) -> str:
    if not isinstance(compound, str):
        raise TypeError(f"compound must be a string, not {type(compound).__name__}.")
    return " ".join(compound.strip().lower().split())


def _normalize_compound_symbol(compound_symbol: str) -> str:
    if not isinstance(compound_symbol, str):
        raise TypeError(f"compound_symbol must be a string, not {type(compound_symbol).__name__}.")
    normalized_compound_symbol = compound_symbol.strip().upper()
    if not normalized_compound_symbol:
        raise ValueError("compound_symbol must be a non-empty string.")
    return normalized_compound_symbol


def _normalize_compound_name(compound_name: str) -> str:
    if not isinstance(compound_name, str):
        raise TypeError(f"compound_name must be a string, not {type(compound_name).__name__}.")
    normalized_compound_name = compound_name.strip()
    if not normalized_compound_name:
        raise ValueError("compound_name must be a non-empty string.")
    return normalized_compound_name


def _merge_override(default_value: float | int, override_value: float | int | None) -> float | int:
    return default_value if override_value is None else override_value


class ChemicalPotentialDefinition(ParameterDefinition):
    def __init__(
        self,
        compound_symbol: str,
        compound_name: str,
        *,
        default_value: float | int | None = None,
        float_format: str | None = None,
        latex_label: str | None = None,
    ) -> None:
        compound_symbol = _normalize_compound_symbol(compound_symbol)
        compound_name = _normalize_compound_name(compound_name)
        super().__init__(
            name=f"mu_{compound_symbol}",
            units="J/ mol",
            label=f"chem. potential of {compound_name}",
            default_value=default_value,
            default_free=0,
            float_format=float_format,
            latex_label=latex_label,
        )


class CarbonChemicalIndexDefinition(ParameterDefinition):
    def __init__(
        self,
        compound_symbol: str,
        compound_name: str,
        *,
        default_value: float | int | None = 1,
        float_format: str | None = None,
        latex_label: str | None = None,
    ) -> None:
        compound_symbol = _normalize_compound_symbol(compound_symbol)
        compound_name = _normalize_compound_name(compound_name)
        super().__init__(
            name=f"n_C{compound_symbol}",
            units="-",
            label=f"chem. index of carbon in {compound_name}",
            default_value=default_value,
            default_free=0,
            float_format=float_format,
            latex_label=latex_label,
        )


class HydrogenChemicalIndexDefinition(ParameterDefinition):
    def __init__(
        self,
        compound_symbol: str,
        compound_name: str,
        *,
        default_value: float | int | None = None,
        float_format: str | None = None,
        latex_label: str | None = None,
    ) -> None:
        compound_symbol = _normalize_compound_symbol(compound_symbol)
        compound_name = _normalize_compound_name(compound_name)
        super().__init__(
            name=f"n_H{compound_symbol}",
            units="-",
            label=f"chem. index of hydrogen in {compound_name}",
            default_value=default_value,
            default_free=0,
            float_format=float_format,
            latex_label=latex_label,
        )


class OxygenChemicalIndexDefinition(ParameterDefinition):
    def __init__(
        self,
        compound_symbol: str,
        compound_name: str,
        *,
        default_value: float | int | None = None,
        float_format: str | None = None,
        latex_label: str | None = None,
    ) -> None:
        compound_symbol = _normalize_compound_symbol(compound_symbol)
        compound_name = _normalize_compound_name(compound_name)
        super().__init__(
            name=f"n_O{compound_symbol}",
            units="-",
            label=f"chem. index of oxygen in {compound_name}",
            default_value=default_value,
            default_free=0,
            float_format=float_format,
            latex_label=latex_label,
        )


class NitrogenChemicalIndexDefinition(ParameterDefinition):
    def __init__(
        self,
        compound_symbol: str,
        compound_name: str,
        *,
        default_value: float | int | None = None,
        float_format: str | None = None,
        latex_label: str | None = None,
    ) -> None:
        compound_symbol = _normalize_compound_symbol(compound_symbol)
        compound_name = _normalize_compound_name(compound_name)
        super().__init__(
            name=f"n_N{compound_symbol}",
            units="-",
            label=f"chem. index of nitrogen in {compound_name}",
            default_value=default_value,
            default_free=0,
            float_format=float_format,
            latex_label=latex_label,
        )


@dataclass(frozen=True)
class ChemicalParameters:
    compound_symbol: str
    compound_name: str
    mu: ChemicalPotentialDefinition
    n_C: CarbonChemicalIndexDefinition
    n_H: HydrogenChemicalIndexDefinition
    n_O: OxygenChemicalIndexDefinition
    n_N: NitrogenChemicalIndexDefinition

    def __post_init__(self) -> None:
        object.__setattr__(self, "compound_symbol", _normalize_compound_symbol(self.compound_symbol))
        object.__setattr__(self, "compound_name", _normalize_compound_name(self.compound_name))

    @property
    def definitions(
        self,
    ) -> tuple[
        ChemicalPotentialDefinition,
        CarbonChemicalIndexDefinition,
        HydrogenChemicalIndexDefinition,
        OxygenChemicalIndexDefinition,
        NitrogenChemicalIndexDefinition,
    ]:
        return (self.mu, self.n_C, self.n_H, self.n_O, self.n_N)

    def as_tuple(
        self,
    ) -> tuple[
        ChemicalPotentialDefinition,
        CarbonChemicalIndexDefinition,
        HydrogenChemicalIndexDefinition,
        OxygenChemicalIndexDefinition,
        NitrogenChemicalIndexDefinition,
    ]:
        return self.definitions


@dataclass(frozen=True)
class ChemicalParameterValues:
    chemical_parameters: ChemicalParameters
    mu: float | int | None = None
    n_C: float | int | None = None
    n_H: float | int | None = None
    n_O: float | int | None = None
    n_N: float | int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.chemical_parameters, ChemicalParameters):
            raise TypeError(
                "chemical_parameters must be a ChemicalParameters instance, "
                f"not {type(self.chemical_parameters).__name__}."
            )

    @classmethod
    def from_common_compound(
        cls,
        compound: str,
        *,
        mu: float | int | None = None,
        n_C: float | int | None = None,
        n_H: float | int | None = None,
        n_O: float | int | None = None,
        n_N: float | int | None = None,
    ) -> "ChemicalParameterValues":
        return get_chemical_parameter_values_of(
            compound,
            mu=mu,
            n_C=n_C,
            n_H=n_H,
            n_O=n_O,
            n_N=n_N,
        )

    @classmethod
    def from_compound(
        cls,
        compound_symbol: str,
        compound_name: str,
        *,
        mu: float | int | None = None,
        n_C: float | int | None = None,
        n_H: float | int | None = None,
        n_O: float | int | None = None,
        n_N: float | int | None = None,
    ) -> "ChemicalParameterValues":
        chemical_parameters = _build_chemical_parameters(compound_symbol, compound_name)
        return cls(
            chemical_parameters=chemical_parameters,
            mu=mu,
            n_C=n_C,
            n_H=n_H,
            n_O=n_O,
            n_N=n_N,
        )

    def iter_supplied_values(self) -> tuple[tuple[ParameterDefinition, float | int], ...]:
        supplied_values: list[tuple[ParameterDefinition, float | int]] = []
        for field_name, definition in (
            ("mu", self.chemical_parameters.mu),
            ("n_C", self.chemical_parameters.n_C),
            ("n_H", self.chemical_parameters.n_H),
            ("n_O", self.chemical_parameters.n_O),
            ("n_N", self.chemical_parameters.n_N),
        ):
            value = getattr(self, field_name)
            if value is not None:
                supplied_values.append((definition, value))
        return tuple(supplied_values)


_CANONICAL_COMPOUNDS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("X", "food", ("x", "food")),
    ("E", "reserve", ("e", "reserve")),
    ("V", "structure", ("v", "structure")),
    ("P", "feces", ("p", "feces", "faeces")),
    ("C", "carbon dioxide", ("c", "carbon dioxide")),
    ("H", "water", ("h", "water")),
    ("O", "oxygen", ("o", "oxygen")),
    ("N", "n-waste", ("n", "n-waste")),
)

_COMPOUND_LOOKUP = {
    alias: (compound_symbol, compound_name)
    for compound_symbol, compound_name, aliases in _CANONICAL_COMPOUNDS
    for alias in aliases
}

_CHEMICAL_VALUE_PRESETS = {
    "food": ("X", "food", 525000, 1, 1.8, 0.5, 0.15),
    "reserve": ("E", "reserve", 550000, 1, 1.8, 0.5, 0.15),
    "structure": ("V", "structure", 500000, 1, 1.8, 0.5, 0.15),
    "feces": ("P", "feces", 480000, 1, 1.8, 0.5, 0.15),
    "carbon dioxide": ("C", "carbon dioxide", 0, 1, 0, 2, 0),
    "water": ("H", "water", 0, 0, 2, 1, 0),
    "oxygen": ("O", "oxygen", 0, 0, 0, 2, 0),
    "ammonia": ("N", "ammonia", 339250, 0, 3, 0, 1),
    "urea": ("N", "urea", 662200, 1, 4, 1, 2),
    "uric acid": ("N", "uric acid", 417480, 1, 0.8, 0.6, 0.8),
    "methane": ("M", "methane", 816000, 1, 4, 0, 0),
}

_CHEMICAL_VALUE_LOOKUP = {
    **{
        alias: "food"
        for alias in ("x", "food")
    },
    **{
        alias: "reserve"
        for alias in ("e", "reserve")
    },
    **{
        alias: "structure"
        for alias in ("v", "structure")
    },
    **{
        alias: "feces"
        for alias in ("p", "feces", "faeces")
    },
    **{
        alias: "carbon dioxide"
        for alias in ("c", "carbon dioxide")
    },
    **{
        alias: "water"
        for alias in ("h", "water")
    },
    **{
        alias: "oxygen"
        for alias in ("o", "oxygen")
    },
    **{
        alias: "ammonia"
        for alias in ("ammonia",)
    },
    **{
        alias: "urea"
        for alias in ("urea",)
    },
    **{
        alias: "uric acid"
        for alias in ("uric acid",)
    },
    **{
        alias: "methane"
        for alias in ("m", "methane")
    },
}


@lru_cache(maxsize=None)
def _build_chemical_parameters(compound_symbol: str, compound_name: str) -> ChemicalParameters:
    return ChemicalParameters(
        compound_symbol=compound_symbol,
        compound_name=compound_name,
        mu=ChemicalPotentialDefinition(compound_symbol, compound_name),
        n_C=CarbonChemicalIndexDefinition(compound_symbol, compound_name),
        n_H=HydrogenChemicalIndexDefinition(compound_symbol, compound_name),
        n_O=OxygenChemicalIndexDefinition(compound_symbol, compound_name),
        n_N=NitrogenChemicalIndexDefinition(compound_symbol, compound_name),
    )


def get_chemical_parameters_of(compound: str) -> ChemicalParameters:
    normalized_compound = _normalize_compound_token(compound)
    resolved_compound = _COMPOUND_LOOKUP.get(normalized_compound)
    if resolved_compound is None:
        raise ValueError(
            f"Unknown chemical compound '{compound}'. Expected one of the standard DEB compounds: "
            "X/food, E/reserve, V/structure, P/feces, C/carbon dioxide, H/water, O/oxygen, N/n-waste."
        )

    compound_symbol, compound_name = resolved_compound
    return _build_chemical_parameters(compound_symbol, compound_name)


def get_chemical_parameter_values_of(
    compound: str,
    *,
    mu: float | int | None = None,
    n_C: float | int | None = None,
    n_H: float | int | None = None,
    n_O: float | int | None = None,
    n_N: float | int | None = None,
) -> ChemicalParameterValues:
    normalized_compound = _normalize_compound_token(compound)
    if normalized_compound in {"n", "n-waste"}:
        raise ValueError(
            "Chemical parameter defaults for 'N'/'n-waste' are ambiguous. "
            "Choose one of: ammonia, urea, or uric acid."
        )

    preset_name = _CHEMICAL_VALUE_LOOKUP.get(normalized_compound)
    if preset_name is None:
        raise ValueError(
            f"Unknown chemical compound '{compound}'. Expected one of the supported compounds with defaults: "
            "X/food, E/reserve, V/structure, P/feces, C/carbon dioxide, H/water, O/oxygen, "
            "ammonia, urea, uric acid, or M/methane."
        )

    compound_symbol, compound_name, default_mu, default_n_C, default_n_H, default_n_O, default_n_N = (
        _CHEMICAL_VALUE_PRESETS[preset_name]
    )
    return ChemicalParameterValues.from_compound(
        compound_symbol=compound_symbol,
        compound_name=compound_name,
        mu=_merge_override(default_mu, mu),
        n_C=_merge_override(default_n_C, n_C),
        n_H=_merge_override(default_n_H, n_H),
        n_O=_merge_override(default_n_O, n_O),
        n_N=_merge_override(default_n_N, n_N),
    )


__all__ = [
    "ChemicalParameterValues",
    "ChemicalParameters",
    "CarbonChemicalIndexDefinition",
    "ChemicalPotentialDefinition",
    "HydrogenChemicalIndexDefinition",
    "NitrogenChemicalIndexDefinition",
    "OxygenChemicalIndexDefinition",
    "get_chemical_parameter_values_of",
    "get_chemical_parameters_of",
]
