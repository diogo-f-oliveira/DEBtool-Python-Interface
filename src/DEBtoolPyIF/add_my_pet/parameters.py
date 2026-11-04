"""Load parameter sets and statistics from Add-my-Pet ``.mat`` files."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy.io

from .cache import fetch_cached_file, get_cache_dir
from .client import AmPClient
from .urls import ampdata_file_url, species_file_url

ALLSTAT_FILE_NAME = "allStat.mat"
ALLSTAT_TAXONOMY_COLUMNS = ("species_en", "family", "order", "class", "phylum", "id_CoL")


@dataclass(frozen=True)
class AmPResults:
    """Contents of an AmP ``results_<species>.mat`` file."""

    species: str
    model: str
    par: dict[str, float]
    free: dict[str, int] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    stats: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_frame(self) -> pd.DataFrame:
        """Parameter table with value, free flag, units and label per parameter."""
        return pd.DataFrame(
            {
                "value": pd.Series(self.par, dtype=float),
                "free": pd.Series(self.free, dtype="Int64"),
                "units": pd.Series(self.units, dtype=object),
                "label": pd.Series(self.labels, dtype=object),
            },
            index=list(self.par),
        ).rename_axis("parameter")


def _load_mat(path: str | os.PathLike) -> dict[str, Any]:
    try:
        return scipy.io.loadmat(path, simplify_cells=True)
    except NotImplementedError as error:
        raise ValueError(
            f"{path} is a MATLAB v7.3 (HDF5) file, which is not supported. "
            "Re-save it in MATLAB with save(..., '-v7')."
        ) from error


def _as_scalar(value: Any) -> float | None:
    if isinstance(value, (bool, np.bool_)):
        return None
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    if isinstance(value, np.ndarray) and value.size == 1 and np.issubdtype(value.dtype, np.number):
        return float(value.item())
    return None


def _as_text(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, np.ndarray) and value.size and all(isinstance(item, str) for item in value.flat):
        return "; ".join(value.flat)
    return None


def _as_date(value: Any) -> str | None:
    values = np.asarray(value).ravel()
    if values.size != 3 or not np.issubdtype(values.dtype, np.number):
        return None
    year, month, day = (int(item) for item in values)
    return f"{year:04d}-{month:02d}-{day:02d}"


def load_results_mat(path: str | os.PathLike) -> AmPResults:
    """Load a ``results_<species>.mat`` file saved by DEBtool's ``estim_pars``."""
    path = Path(path)
    content = _load_mat(path)
    if "par" not in content:
        raise ValueError(f"{path} does not contain a 'par' struct; is it a DEBtool results file?")

    raw_par = dict(content["par"])
    raw_free = raw_par.pop("free", {}) or {}
    par = {name: scalar for name, value in raw_par.items() if (scalar := _as_scalar(value)) is not None}
    free = {name: int(scalar) for name, value in raw_free.items() if (scalar := _as_scalar(value)) is not None}

    txt_par = content.get("txtPar", {}) or {}
    units = {name: text for name, value in (txt_par.get("units") or {}).items() if (text := _as_text(value))}
    labels = {name: text for name, value in (txt_par.get("label") or {}).items() if (text := _as_text(value))}

    stats = dict(content.get("metaPar", {}) or {})
    model = _as_text(stats.pop("model", None)) or ""
    metadata = dict(content.get("metaData", {}) or {})

    prefix = "results_"
    default_species = path.stem[len(prefix):] if path.stem.startswith(prefix) else path.stem
    species = _as_text(metadata.get("species")) or default_species

    return AmPResults(
        species=species, model=model, par=par, free=free, units=units, labels=labels, stats=stats, metadata=metadata,
    )


def load_allstat(path: str | os.PathLike) -> pd.DataFrame:
    """Load the AmP ``allStat.mat`` file as a table with one row per species.

    Columns are the taxonomy (``species_en``, ``family``, ``order``, ``class``, ``phylum``, ``id_CoL``), ``model``,
    ``MRE``, ``SMSE``, ``completeness``, ``date_update``, ``date_submission`` and every other scalar numeric
    statistic (parameters and implied properties). Missing values are NaN.
    """
    content = _load_mat(path)
    if "allStat" not in content:
        raise ValueError(f"{path} does not contain an 'allStat' struct.")

    rows = {}
    for species, stat in content["allStat"].items():
        row: dict[str, Any] = {column: _as_text(stat.get(column)) for column in ALLSTAT_TAXONOMY_COLUMNS}
        row["model"] = _as_text(stat.get("model"))
        row["MRE"] = _as_scalar(stat.get("MRE"))
        row["SMSE"] = _as_scalar(stat.get("SMSE"))
        row["completeness"] = _as_scalar(stat.get("COMPLETE"))
        row["date_update"] = _as_date(stat.get("date_acc", []))
        row["date_submission"] = _as_date(stat.get("date_subm", []))
        for name, value in stat.items():
            if name in row or name == "COMPLETE":
                continue
            scalar = _as_scalar(value)
            if scalar is not None:
                row[name] = scalar
        rows[species] = row

    table = pd.DataFrame.from_dict(rows, orient="index")
    table.index.name = "species"
    return table


def fetch_species_parameters(
        species: str,
        cache_dir: str | os.PathLike | None = None,
        *,
        check_update: bool = False,
        client: AmPClient | None = None,
) -> AmPResults:
    """Load the parameter set of ``species`` from AmP, downloading ``results_<species>.mat`` if it is not cached.

    @param cache_dir: folder where files are cached, see ``get_cache_dir``.
    @param check_update: if True, ask AmP whether the entry changed and refresh the cached copy if so. By default
        a cached copy is reused as-is, so repeated runs return the same parameters.
    """
    client = AmPClient() if client is None else client
    file_name = f"results_{species}.mat"
    path = fetch_cached_file(
        client,
        species_file_url(species, file_name, client.base_url),
        get_cache_dir(cache_dir) / species / file_name,
        check_update=check_update,
    )
    return load_results_mat(path)


def fetch_allstat(
        cache_dir: str | os.PathLike | None = None,
        *,
        check_update: bool = False,
        client: AmPClient | None = None,
) -> pd.DataFrame:
    """Load the AmP ``allStat.mat`` table with ``load_allstat``, downloading it if it is not cached.

    @param cache_dir: folder where files are cached, see ``get_cache_dir``.
    @param check_update: if True, ask AmP whether the file changed and refresh the cached copy if so.
    """
    client = AmPClient() if client is None else client
    path = fetch_cached_file(
        client,
        ampdata_file_url(ALLSTAT_FILE_NAME, client.base_url),
        get_cache_dir(cache_dir) / ALLSTAT_FILE_NAME,
        check_update=check_update,
    )
    return load_allstat(path)
