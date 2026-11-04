"""Download species estimation files from the Add-my-Pet collection."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from tqdm.auto import tqdm

from .client import AmPClient, DownloadStatus

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

    @property
    def ok(self) -> bool:
        return self.listing_error is None and not self.errors

    def paths(self) -> dict[str, Path]:
        """Local paths of the files that are present after the download."""
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


def download_species(
        species: str,
        dest_folder: str | os.PathLike,
        *,
        files: Iterable[str] | None = None,
        overwrite: bool = False,
        check_update: bool = False,
        client: AmPClient | None = None,
) -> SpeciesDownloadReport:
    """Download the AmP estimation files of ``species`` into ``dest_folder/<species>/``.

    @param files: files to download, either file names or the short keys ``mydata``, ``pars_init``, ``predict``,
        ``run`` and ``results``. If None, every estimation file in the species entry is downloaded.
    @param overwrite: if True, existing local files are always replaced.
    @param check_update: if True, existing local files are replaced when the AmP version is newer.
    @param client: AmPClient to reuse; a new one is created if None.
    Download errors are recorded in the returned report instead of being raised.
    """
    client = AmPClient() if client is None else client
    report = SpeciesDownloadReport(species=species, folder=Path(dest_folder) / species)

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
    return report


def download_amp_database(
        dest_folder: str | os.PathLike,
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

    @param dest_folder: main output folder; each species is saved in its own subfolder.
    @param species: species to download. If None, every species in the AmP collection is downloaded.
    @param files: files to download per species, see ``download_species``.
    @param overwrite: if True, existing local files are always replaced.
    @param check_update: if True, existing local files are replaced when the AmP version is newer.
    @param max_workers: maximum number of parallel download threads.
    @param progress: if True, show a progress bar.
    @return: report per species, in the order species were requested.
    """
    client = AmPClient() if client is None else client
    species = client.list_species() if species is None else list(species)
    files = None if files is None else list(files)

    reports = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_species = {
            executor.submit(
                download_species, name, dest_folder,
                files=files, overwrite=overwrite, check_update=check_update, client=client,
            ): name
            for name in species
        }
        futures = as_completed(future_to_species)
        if progress:
            futures = tqdm(futures, total=len(future_to_species), desc="Downloading species")
        for future in futures:
            name = future_to_species[future]
            reports[name] = future.result()
            if progress and not reports[name].ok:
                tqdm.write(f"Errors downloading species {name}: {reports[name].listing_error or reports[name].errors}")
    return {name: reports[name] for name in species}
