"""Bootstrap estimation workflows from existing Add-my-Pet entries."""

from __future__ import annotations

import os

from ..estimation_files.config import FILE_KEYS, EstimationTemplates
from ..estimation_files.templates import CopyFileTemplate
from .client import AmPClient, DownloadStatus
from .download import SPECIES_FILE_PATTERNS, download_species


def bootstrap_species(
        species: str,
        dest_folder: str | os.PathLike,
        *,
        overwrite: bool = False,
        check_update: bool = False,
        client: AmPClient | None = None,
) -> EstimationTemplates:
    """Download an AmP species entry and wrap its files as ``EstimationTemplates``.

    The four species files (and ``results_<species>.mat`` when available) are saved in
    ``dest_folder/<species>/``. Each species file is wrapped verbatim in a ``CopyFileTemplate``, so the returned
    object can be used directly for a single-species estimation or as the starting point for adapting the files
    into substitution templates for a multitier workflow.

    @raise RuntimeError: if any of the four species files could not be downloaded.
    """
    report = download_species(
        species,
        dest_folder,
        files=(*FILE_KEYS, "results"),
        overwrite=overwrite,
        check_update=check_update,
        client=client,
    )
    file_names = {key: SPECIES_FILE_PATTERNS[key].format(species=species) for key in FILE_KEYS}
    missing = {
        file_name: report.errors.get(file_name, "")
        for file_name in file_names.values()
        if report.files.get(file_name) is DownloadStatus.FAILED
    }
    if missing:
        raise RuntimeError(f"Could not download the AmP files of species '{species}': {missing}")

    return EstimationTemplates(
        **{key: CopyFileTemplate(report.folder / file_name) for key, file_name in file_names.items()}
    )
