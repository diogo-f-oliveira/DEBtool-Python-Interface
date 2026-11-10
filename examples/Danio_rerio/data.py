"""Mock species-level data for the Danio_rerio single-species example.

All values are MOCK data: they were generated from the std model with a known parameter set (``MOCK_TRUE_PARS``)
and perturbed by up to ~6% and rounded, so the example can be run end to end before the real dataset is chosen. Do not use them
for anything biological.

The package has no data-source classes for species-level (zero-variate and univariate) data yet; see
"Data-source classes for zero-variate species data" in ``docs/ROADMAP.md``. ``ZeroVariateData``,
``UnivariateData`` and ``SpeciesDataSection`` below are a prototype of that API, kept in the example until the
design is settled.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from DEBtoolPyIF.estimation_files import MyDataSection
from DEBtoolPyIF.utils.data_conversion import (
    convert_list_of_strings_to_matlab,
    convert_numeric_array_to_matlab,
    convert_string_to_matlab,
)
from DEBtoolPyIF.utils.mydata_code_generation import generate_aux_data_code, generate_data_code

MOCK_BIBKEY = "mock"
TEMPERATURE_K = 273.15 + 28.5  # K, standard zebrafish rearing temperature

# Parameters used to generate the mock data (std model). The estimation starts from INITIAL_PARS instead.
MOCK_TRUE_PARS = {
    "z": 0.8,
    "kap_X": 0.8,
    "kap_P": 0.1,
    "v": 0.02,
    "kap": 0.6,
    "p_M": 300.0,
    "E_G": 5200.0,
    "E_Hb": 0.5,
    "E_Hp": 2000.0,
    "h_a": 2e-9,
    "del_M": 0.2,
}


@dataclass(frozen=True)
class ZeroVariateData:
    """One zero-variate dataset (a single value), e.g. age at birth."""

    name: str
    value: float
    units: str
    label: str
    temperature: float | None = None  # K
    bibkey: str = MOCK_BIBKEY
    comment: str = "mock data"

    def generate_mydata_code(self) -> str:
        code = generate_data_code(
            var_name=self.name,
            converted_data=convert_numeric_array_to_matlab(self.value),
            units=convert_string_to_matlab(self.units),
            label=convert_string_to_matlab(self.label),
            bibkey=self.bibkey,
            comment=self.comment,
        )
        return code + _temperature_code(self.name, self.temperature)


@dataclass(frozen=True)
class UnivariateData:
    """One univariate dataset: a two-column array of independent and dependent values."""

    name: str
    values: np.ndarray
    units: tuple[str, str]
    label: tuple[str, str]
    title: str
    temperature: float | None = None  # K
    bibkey: str = MOCK_BIBKEY
    comment: str = "mock data"

    def generate_mydata_code(self) -> str:
        values = np.asarray(self.values, dtype=float)
        if values.ndim != 2 or values.shape[1] != 2:
            raise ValueError(f"Univariate dataset '{self.name}' must be an (n, 2) array.")
        code = generate_data_code(
            var_name=self.name,
            converted_data=convert_numeric_array_to_matlab(values),
            units=convert_list_of_strings_to_matlab(list(self.units)),
            label=convert_list_of_strings_to_matlab(list(self.label)),
            title=self.title,
            bibkey=self.bibkey,
            comment=self.comment,
        )
        return code + _temperature_code(self.name, self.temperature)


def _temperature_code(name: str, temperature: float | None) -> str:
    if temperature is None:
        return "\n"
    return generate_aux_data_code(
        var_name=name,
        converted_data=convert_numeric_array_to_matlab(temperature),
        struct_name="temp",
        label=convert_string_to_matlab("temperature"),
        units=convert_string_to_matlab("K"),
    )


class SpeciesDataSection(MyDataSection):
    """Render species-level zero-variate and univariate datasets into mydata.m."""

    key = "species_data_block"
    template_families = ("mydata",)

    def __init__(self, datasets: tuple[ZeroVariateData | UnivariateData, ...] = ()) -> None:
        self.datasets = tuple(datasets)
        names = [dataset.name for dataset in self.datasets]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(f"Duplicate dataset names: {', '.join(duplicates)}.")
        super().__init__()

    def render(self, _context, _state) -> str:
        zero_variate = [d for d in self.datasets if isinstance(d, ZeroVariateData)]
        univariate = [d for d in self.datasets if isinstance(d, UnivariateData)]
        blocks = ["%% set data", "% zero-variate data"]
        blocks += [dataset.generate_mydata_code() for dataset in zero_variate]
        blocks += ["% uni-variate data"]
        blocks += [dataset.generate_mydata_code() for dataset in univariate]
        return "\n".join(blocks)


def load_mock_datasets() -> tuple[ZeroVariateData | UnivariateData, ...]:
    """Return the mock zebrafish datasets used by the example."""

    T = TEMPERATURE_K
    zero_variate = (
        ZeroVariateData("ab", 4.0, "d", "age at birth", temperature=T),
        ZeroVariateData("tp", 75.0, "d", "time since birth at puberty", temperature=T),
        ZeroVariateData("am", 1040.0, "d", "life span", temperature=T),
        ZeroVariateData("Lb", 0.26, "cm", "total length at birth"),
        ZeroVariateData("Lp", 2.5, "cm", "total length at puberty"),
        ZeroVariateData("Li", 4.1, "cm", "ultimate total length"),
        ZeroVariateData("Wwb", 6.6e-4, "g", "wet weight at birth"),
        ZeroVariateData("Wwi", 2.6, "g", "ultimate wet weight"),
        ZeroVariateData("Ri", 56.0, "#/d", "maximum reproduction rate", temperature=T),
    )
    univariate = (
        UnivariateData(
            "tL",
            values=np.array([[0.0, 0.26], [30.0, 1.4], [60.0, 2.3], [90.0, 2.7], [150.0, 3.5], [240.0, 3.75]]),
            units=("d", "cm"),
            label=("time since birth", "total length"),
            title="mock growth curve",
            temperature=T,
        ),
        UnivariateData(
            "LW",
            values=np.array([[1.0, 0.044], [2.0, 0.33], [3.0, 1.2], [4.0, 2.65]]),
            units=("cm", "g"),
            label=("total length", "wet weight"),
            title="mock length-weight relationship",
        ),
    )
    return zero_variate + univariate
