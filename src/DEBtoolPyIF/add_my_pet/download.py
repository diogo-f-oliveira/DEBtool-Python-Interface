"""Download species estimation files from the Add-my-Pet collection."""

from __future__ import annotations

import os
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests
from tqdm.auto import tqdm

from .client import AmPClient, DownloadStatus
from .manifest import (
    ALLSTAT_ENTRY,
    ManifestEntry,
    current_timestamp,
    read_amp_version,
    read_complete_species,
    resolve_folder,
    split_manifest_files,
    update_manifest,
)
from .urls import ampdata_file_url, species_dir_url

ALLSTAT_FILE_NAME = "allStat.mat"

_CONNECTION_ERRORS = (requests.ConnectionError, requests.Timeout)
# Downloads of at least this many species print a notice with the expected duration
_LONG_DOWNLOAD_SPECIES = 50
_TYPICAL_FILES_PER_SPECIES = 6

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
    connection_failed: bool = False
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
            report.connection_failed = isinstance(error, _CONNECTION_ERRORS)
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
            if isinstance(error, _CONNECTION_ERRORS):
                # The remaining files would only wait for the same timeout
                report.connection_failed = True
                break

    report.amp_version = read_amp_version(report.folder, species)
    return report


def _manifest_entry(
        report: SpeciesDownloadReport, client: AmPClient, all_files: bool
) -> ManifestEntry | None:
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
        # Only a download of every file in the entry can show that the species is complete
        complete=report.ok if all_files else None,
    )


def _uses_manifest(files: Iterable[str] | None, overwrite: bool, check_update: bool) -> bool:
    """Whether species the manifest records as complete can be skipped without contacting AmP."""
    return files is None and not overwrite and not check_update


def _report_from_manifest(species: str, folder: Path, row: dict[str, str] | None) -> SpeciesDownloadReport | None:
    """Return a report for a species the manifest records as complete, or None if it has to be downloaded.

    The species is only skipped if every file the manifest lists for it is still in its folder.
    """
    if row is None:
        return None
    species_folder = folder / species
    file_names = split_manifest_files(row["files"])
    if not file_names or not all((species_folder / file_name).is_file() for file_name in file_names):
        return None
    return SpeciesDownloadReport(
        species=species,
        folder=species_folder,
        files={file_name: DownloadStatus.SKIPPED_EXISTS for file_name in file_names},
        amp_version=row.get("amp_version") or None,
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
    ``amp_manifest.csv`` of ``folder``, including its AmP version. If the manifest records an earlier download of
    every file of the species as complete and those files are still in ``folder``, AmP is not contacted, unless
    ``files``, ``overwrite`` or ``check_update`` is given.
    """
    client = AmPClient() if client is None else client
    folder = resolve_folder(folder)
    if _uses_manifest(files, overwrite, check_update):
        report = _report_from_manifest(species, folder, read_complete_species(folder).get(species))
        if report is not None:
            return report
    report = _download_species_files(species, folder, files, overwrite, check_update, client)
    entry = _manifest_entry(report, client, all_files=files is None)
    update_manifest(folder, [] if entry is None else [entry])
    return report


def download_allstat(
        folder: str | os.PathLike | None = None,
        *,
        overwrite: bool = False,
        check_update: bool = False,
        client: AmPClient | None = None,
) -> Path:
    """Download the AmP ``allStat.mat`` file into ``folder`` and return its path.

    @param folder: folder to save into. If None, the default folder from ``get_cache_dir`` is used.
    @param overwrite: if True, an existing local file is always replaced.
    @param check_update: if True, an existing local file is replaced when the AmP version is newer.
    @param client: AmPClient to reuse; a new one is created if None.
    Unlike ``download_species``, download errors are raised, as ``requests.RequestException``.
    """
    client = AmPClient() if client is None else client
    folder = resolve_folder(folder)
    status = client.download_ampdata_file(ALLSTAT_FILE_NAME, folder, overwrite=overwrite, check_update=check_update)
    path = folder / ALLSTAT_FILE_NAME
    # allStat has no entry date, so its version is the date AmP last published the file
    version = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y%m%d")
    transferred = status in (DownloadStatus.DOWNLOADED, DownloadStatus.UPDATED)
    update_manifest(folder, [ManifestEntry(
        species=ALLSTAT_ENTRY,
        files=(ALLSTAT_FILE_NAME,),
        source_url=ampdata_file_url(ALLSTAT_FILE_NAME, client.base_url),
        amp_version=version,
        downloaded_at=current_timestamp() if transferred else None,
    )])
    return path


def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return "less than a minute"
    if seconds < 90 * 60:
        return f"about {round(seconds / 60)} minutes"
    return f"about {seconds / 3600:.1f} hours"


def _print_long_download_notice(n_species: int, folder: Path, n_files: int | None, client: AmPClient) -> None:
    # A listing request per species when all of its files are requested
    requests_per_species = _TYPICAL_FILES_PER_SPECIES + 1 if n_files is None else n_files
    duration = _format_duration(n_species * requests_per_species * client.request_delay)
    print(
        f"Downloading {n_species} AmP species into {folder}.\n"
        f"The AmP server can stop responding after many requests, so requests are sent {client.request_delay} s apart."
        f" This can take {duration}, less for files you already have.\n"
        "If the server stops responding the download stops, and you can rerun it later to continue."
    )


def download_amp_collection(
        folder: str | os.PathLike | None = None,
        species: Iterable[str] | None = None,
        *,
        files: Iterable[str] | None = None,
        overwrite: bool = False,
        check_update: bool = False,
        max_workers: int = 2,
        max_connection_failures: int = 3,
        progress: bool = True,
        client: AmPClient | None = None,
) -> dict[str, SpeciesDownloadReport]:
    """Download the estimation files of many species.

    Requests are paced by the client (see ``AmPClient.request_delay``) because the AmP server stops accepting
    connections after many requests. If it stops responding, the download stops with a warning. Rerun the same call
    later to continue: files already in ``folder`` are not downloaded again, and species the manifest records as
    complete are skipped without contacting AmP. Pass ``check_update=True`` to check every species for newer files.

    @param folder: folder to save into, with one subfolder per species. If None, the default folder from
        ``get_cache_dir`` is used.
    @param species: species to download. If None, every species in the AmP collection is downloaded.
    @param files: files to download per species, see ``download_species``.
    @param overwrite: if True, existing local files are always replaced.
    @param check_update: if True, existing local files are replaced when the AmP version is newer.
    @param max_workers: maximum number of parallel download threads.
    @param max_connection_failures: stop after this many species in a row fail to connect.
    @param progress: if True, show a progress bar and, for large downloads, a notice with the expected duration.
    @return: report per species that was attempted, in the order species were requested.
    """
    client = AmPClient() if client is None else client
    folder = resolve_folder(folder)
    species = client.list_species() if species is None else list(species)
    files = None if files is None else list(files)

    reports = {}
    species_to_download = species
    if _uses_manifest(files, overwrite, check_update):
        complete_rows = read_complete_species(folder)
        species_to_download = []
        for name in species:
            report = _report_from_manifest(name, folder, complete_rows.get(name))
            if report is None:
                species_to_download.append(name)
            else:
                reports[name] = report
        if progress and reports:
            print(f"Skipping {len(reports)} species already complete in {folder}.")
    skipped_species = set(reports)
    if progress and len(species_to_download) >= _LONG_DOWNLOAD_SPECIES:
        _print_long_download_notice(len(species_to_download), folder, None if files is None else len(files), client)

    future_to_species = {}
    connection_failures = 0
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for name in species_to_download:
                future = executor.submit(_download_species_files, name, folder, files, overwrite, check_update, client)
                future_to_species[future] = name
            futures = as_completed(future_to_species)
            if progress:
                futures = tqdm(futures, total=len(future_to_species), desc="Downloading species")
            try:
                for future in futures:
                    name = future_to_species[future]
                    reports[name] = future.result()
                    if progress and not reports[name].ok:
                        tqdm.write(
                            f"Errors downloading species {name}: "
                            f"{reports[name].listing_error or reports[name].errors}"
                        )
                    connection_failures = connection_failures + 1 if reports[name].connection_failed else 0
                    if connection_failures >= max_connection_failures:
                        break
            finally:
                for future in future_to_species:
                    future.cancel()
    finally:
        # Written once at the end, and also if the run is interrupted, so finished species are always recorded
        for future, name in future_to_species.items():
            if name not in reports and future.done() and not future.cancelled():
                reports[name] = future.result()
        entries = (
            _manifest_entry(report, client, all_files=files is None)
            for name, report in reports.items()
            if name not in skipped_species
        )
        update_manifest(folder, [entry for entry in entries if entry is not None])

    if connection_failures >= max_connection_failures:
        warnings.warn(
            f"The AmP server stopped responding, so the download stopped after {len(reports)} of {len(species)} "
            "species. This is usually temporary. Wait a few hours and run the same command again to continue."
        )
    return {name: reports[name] for name in species if name in reports}
