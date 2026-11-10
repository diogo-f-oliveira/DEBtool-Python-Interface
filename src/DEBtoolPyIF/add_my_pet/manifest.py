"""Folders of Add-my-Pet files and the manifest recording what each one contains.

Every folder holds one ``amp_manifest.csv`` with a row per species: its AmP version, files, download time, source and
whether its last full download finished without errors.
The AmP version is the entry's acceptance date as ``yyyymmdd``, the same date AmP uses to name and archive its
entries (``<species>_<yyyymmdd>.zip``), so it can be cited and looked up on the AmP website.
"""

from __future__ import annotations

import os
import re
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import platformdirs
import scipy.io

CACHE_DIR_ENV_VAR = "DEBTOOLPYIF_AMP_CACHE"
MANIFEST_FILE_NAME = "amp_manifest.csv"
MANIFEST_COLUMNS = ("species", "amp_version", "files", "downloaded_at", "source_url", "complete")
ALLSTAT_ENTRY = "allStat"

_FILE_SEPARATOR = ";"
_DATE_ACC_PATTERN = re.compile(
    r"^[ \t]*metaData\.date_acc\s*=\s*\[\s*(\d{4})[\s,;]+(\d+)[\s,;]+(\d+)",
    re.MULTILINE,
)


@dataclass(frozen=True)
class ManifestEntry:
    """Update to one manifest row. ``files`` are added to the row; None values keep what the row already has."""

    species: str
    files: tuple[str, ...]
    source_url: str
    amp_version: str | None = None
    downloaded_at: str | None = None
    # Whether a download of every file in the entry finished without errors; None keeps the row's value
    complete: bool | None = None


def get_cache_dir() -> Path:
    """Return the folder used when no folder is given.

    This is the ``DEBTOOLPYIF_AMP_CACHE`` environment variable if set, otherwise the operating system's user cache
    folder (e.g. ``%LOCALAPPDATA%\\DEBtoolPyIF\\Cache\\add_my_pet`` on Windows).
    """
    env_dir = os.environ.get(CACHE_DIR_ENV_VAR)
    if env_dir:
        return Path(env_dir)
    return Path(platformdirs.user_cache_dir("DEBtoolPyIF", appauthor=False)) / "add_my_pet"


def resolve_folder(folder: str | os.PathLike | None) -> Path:
    return get_cache_dir() if folder is None else Path(folder)


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def date_to_amp_version(date: Any) -> str | None:
    """Convert a ``[year, month, day]`` date to the ``yyyymmdd`` AmP version."""
    values = np.asarray(date).ravel()
    if values.size != 3 or not np.issubdtype(values.dtype, np.number):
        return None
    year, month, day = (int(value) for value in values)
    return f"{year:04d}{month:02d}{day:02d}"


def _version_from_mydata(path: Path) -> str | None:
    match = _DATE_ACC_PATTERN.search(path.read_text(encoding="utf-8", errors="replace"))
    return date_to_amp_version([int(value) for value in match.groups()]) if match else None


def _version_from_results(path: Path) -> str | None:
    content = scipy.io.loadmat(path, simplify_cells=True, variable_names=["metaData"])
    return date_to_amp_version(content.get("metaData", {}).get("date_acc", []))


def read_amp_version(species_folder: str | os.PathLike, species: str) -> str | None:
    """Return the AmP version of the files in ``species_folder``, or None if it cannot be determined.

    The version is read from ``mydata_<species>.m`` and ``results_<species>.mat``, whichever exist. If they differ
    because only one was updated, the most recent one is returned.
    """
    species_folder = Path(species_folder)
    readers = (
        (species_folder / f"mydata_{species}.m", _version_from_mydata),
        (species_folder / f"results_{species}.mat", _version_from_results),
    )
    versions = []
    for path, reader in readers:
        if not path.exists():
            continue
        # The version is informative only; an unreadable file must not fail the download
        try:
            versions.append(reader(path))
        except Exception:
            continue
    versions = [version for version in versions if version]
    return max(versions) if versions else None


def read_manifest(folder: str | os.PathLike | None = None) -> pd.DataFrame:
    """Return the manifest of ``folder`` (the default folder if None) as a table; empty if it has no manifest."""
    path = resolve_folder(folder) / MANIFEST_FILE_NAME
    if not path.exists():
        return pd.DataFrame(columns=list(MANIFEST_COLUMNS), dtype=str)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _write_manifest(folder: Path, rows: dict[str, dict[str, str]]) -> None:
    path = folder / MANIFEST_FILE_NAME
    temporary_path = path.with_name(path.name + ".part")
    table = pd.DataFrame(
        [rows[species] for species in sorted(rows)],
        columns=list(MANIFEST_COLUMNS),
    )
    folder.mkdir(parents=True, exist_ok=True)
    table.to_csv(temporary_path, index=False)
    try:
        os.replace(temporary_path, path)
    except PermissionError:
        # Spreadsheet programs lock open files on Windows; the downloaded files themselves are fine
        temporary_path.unlink()
        warnings.warn(f"Could not update {path}. Close it if it is open in another program and download again.")


def update_manifest(folder: Path, entries: Iterable[ManifestEntry]) -> None:
    """Merge ``entries`` into the manifest of ``folder``."""
    entries = list(entries)
    if not entries:
        return
    rows = {row["species"]: row for row in read_manifest(folder).to_dict("records")}
    for entry in entries:
        previous = rows.get(entry.species, {})
        files = set(previous.get("files", "").split(_FILE_SEPARATOR)) | set(entry.files)
        rows[entry.species] = {
            "species": entry.species,
            "amp_version": entry.amp_version or previous.get("amp_version", ""),
            "files": _FILE_SEPARATOR.join(sorted(files - {""})),
            "downloaded_at": entry.downloaded_at or previous.get("downloaded_at", ""),
            "source_url": entry.source_url,
            "complete": previous.get("complete", "") if entry.complete is None else ("yes" if entry.complete else "no"),
        }
    _write_manifest(folder, rows)


def read_complete_species(folder: Path) -> dict[str, dict[str, str]]:
    """Return the manifest rows of species whose last full download finished without errors, keyed by species."""
    return {
        row["species"]: row
        for row in read_manifest(folder).to_dict("records")
        if row.get("complete") == "yes"
    }


def split_manifest_files(value: str) -> list[str]:
    """Split the ``files`` value of a manifest row into file names."""
    return [file_name for file_name in value.split(_FILE_SEPARATOR) if file_name]


def clear_cache(species: str | Iterable[str] | None = None) -> list[Path]:
    """Delete files from the default folder (see ``get_cache_dir``) and return the deleted paths.

    @param species: species to delete, or ``"allStat"`` for the allStat table. If None, everything is deleted.
    Only files listed in the manifest are deleted, so anything else in the folder is left alone. Folders chosen by
    the user are never touched: delete those files directly.
    """
    folder = get_cache_dir()
    rows = {row["species"]: row for row in read_manifest(folder).to_dict("records")}
    if species is None:
        selected = list(rows)
    else:
        selected = [species] if isinstance(species, str) else list(species)

    removed = []
    for name in selected:
        row = rows.pop(name, None)
        if row is None:
            continue
        entry_folder = folder if name == ALLSTAT_ENTRY else folder / name
        for file_name in row["files"].split(_FILE_SEPARATOR):
            path = entry_folder / file_name
            if path.is_file():
                path.unlink()
                removed.append(path)
        if entry_folder != folder and entry_folder.is_dir() and not any(entry_folder.iterdir()):
            entry_folder.rmdir()

    if rows:
        _write_manifest(folder, rows)
    elif (folder / MANIFEST_FILE_NAME).exists():
        (folder / MANIFEST_FILE_NAME).unlink()
    return removed
