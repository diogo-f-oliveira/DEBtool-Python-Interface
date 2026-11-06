"""Download species estimation files from the Add-my-Pet collection."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from tqdm.auto import tqdm

from .client import AmPClient, DownloadStatus
from .manifest import ManifestEntry, current_timestamp, read_amp_version, resolve_folder, update_manifest
from .urls import species_dir_url

# Short keys accepted by ``download_species(files=...)``, expanded with the species name
SPECIES_FILE_PATTERNS = {
    "mydata": "mydata_{species}.m",
    "pars_init": "pars_init_{species}.m",
    "predict": "predict_{species}.m",
    "run": "run_{species}.m",
    "results": "results_{species}.mat",
}


@dataclass
class SpeciesDownloadReport:
    """Per-file outcome of downloading one species."""

    species: str
    folder: Path
    files: dict[str, DownloadStatus] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    listing_error: str | None = None
    amp_version: str | None = None

    @property
    def ok(self) -> bool:
        return self.listing_error is None and not self.errors

    def paths(self) -> dict[str, Path]:
        """Local paths of the files that were downloaded or were already up to date."""
        return {
            file_name: self.folder / file_name
            for file_name, status in self.files.items()
            if status is not DownloadStatus.FAILED
        }


def resolve_species_file_names(species: str, files: Iterable[str]) -> list[str]:
    """Expand short keys (``mydata``, ``pars_init``, ``predict``, ``run``, ``results``) to file names."""
    return [
        SPECIES_FILE_PATTERNS[file].format(species=species) if file in SPECIES_FILE_PATTERNS else file
        for file in files
    ]


def _download_species_files(
        species: str,
        folder: Path,
        files: Iterable[str] | None,
        overwrite: bool,
        check_update: bool,
        client: AmPClient,
) -> SpeciesDownloadReport:
    report = SpeciesDownloadReport(species=species, folder=folder / species)

    if files is None:
        try:
            file_names = client.list_species_files(species)
        except Exception as error:
            report.listing_error = str(error)
            return report
    else:
        file_names = resolve_species_file_names(species, files)

    for file_name in file_names:
        try:
            report.files[file_name] = client.download_species_file(
                species, file_name, report.folder, overwrite=overwrite, check_update=check_update
            )
        except Exception as error:
            report.files[file_name] = DownloadStatus.FAILED
            report.errors[file_name] = str(error)

    report.amp_version = read_amp_version(report.folder, species)
    return report


def _manifest_entry(report: SpeciesDownloadReport, client: AmPClient) -> ManifestEntry | None:
    file_names = report.paths()
    if not file_names:
        return None
    transferred = any(
        status in (DownloadStatus.DOWNLOADED, DownloadStatus.UPDATED) for status in report.files.values()
    )
    return ManifestEntry(
        species=report.species,
        files=tuple(file_names),
        source_url=species_dir_url(report.species, client.base_url),
        amp_version=report.amp_version,
        downloaded_at=current_timestamp() if transferred else None,
    )


def download_species(
        species: str,
        folder: str | os.PathLike | None = None,
        *,
        files: Iterable[str] | None = None,
        overwrite: bool = False,
        check_update: bool = False,
        client: AmPClient | None = None,
) -> SpeciesDownloadReport:
    """Download the AmP estimation files of ``species`` into ``folder/<species>/``.

    @param folder: folder to save into. If None, the default folder from ``get_cache_dir`` is used.
    @param files: files to download, either file names or the short keys ``mydata``, ``pars_init``, ``predict``,
        ``run`` and ``results``. If None, every file in the species entry except result figures is downloaded.
    @param overwrite: if True, existing local files are always replaced.
    @param check_update: if True, existing local files are replaced when the AmP version is newer.
    @param client: AmPClient to reuse; a new one is created if None.
    Download errors are recorded in the returned report instead of being raised. The species is recorded in the
    ``amp_manifest.csv`` of ``folder``, including its AmP version.
    """
    client = AmPClient() if client is None else client
    folder = resolve_folder(folder)
    report = _download_species_files(species, folder, files, overwrite, check_update, client)
    entry = _manifest_entry(report, client)
    update_manifest(folder, [] if entry is None else [entry])
    return report


def download_amp_collection(
        folder: str | os.PathLike | None = None,
        species: Iterable[str] | None = None,
        *,
        files: Iterable[str] | None = None,
        overwrite: bool = False,
        check_update: bool = False,
        max_workers: int = 8,
        progress: bool = True,
        client: AmPClient | None = None,
) -> dict[str, SpeciesDownloadReport]:
    """Download the estimation files of many species in parallel, one species per thread.

    @param folder: folder to save into, with one subfolder per species. If None, the default folder from
        ``get_cache_dir`` is used.
    @param species: species to download. If None, every species in the AmP collection is downloaded.
    @param files: files to download per species, see ``download_species``.
    @param overwrite: if True, existing local files are always replaced.
    @param check_update: if True, existing local files are replaced when the AmP version is newer.
    @param max_workers: maximum number of parallel download threads.
    @param progress: if True, show a progress bar.
    @return: report per species, in the order species were requested.
    """
    client = AmPClient() if client is None else client
    folder = resolve_folder(folder)
    species = client.list_species() if species is None else list(species)
    files = None if files is None else list(files)

    reports = {}
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_species = {
                executor.submit(_download_species_files, name, folder, files, overwrite, check_update, client): name
                for name in species
            }
            futures = as_completed(future_to_species)
            if progress:
                futures = tqdm(futures, total=len(future_to_species), desc="Downloading species")
            for future in futures:
                name = future_to_species[future]
                reports[name] = future.result()
                if progress and not reports[name].ok:
                    tqdm.write(
                        f"Errors downloading species {name}: {reports[name].listing_error or reports[name].errors}"
                    )
    finally:
        # Written once at the end, and also if the run is interrupted, so finished species are always recorded
        entries = (_manifest_entry(report, client) for report in reports.values())
        update_manifest(folder, [entry for entry in entries if entry is not None])
    return {name: reports[name] for name in species}
