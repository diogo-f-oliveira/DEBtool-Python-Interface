"""Bootstrap estimation workflows from existing Add-my-Pet entries."""

from __future__ import annotations

import os

import requests

from ..estimation_files.config import FILE_KEYS, EstimationTemplates
from ..estimation_files.templates import CopyFileTemplate
from .client import AmPClient, DownloadStatus
from .download import download_species, resolve_species_file_names


def bootstrap_species(
        species: str,
        folder: str | os.PathLike,
        *,
        overwrite: bool = False,
        check_update: bool = False,
        client: AmPClient | None = None,
) -> EstimationTemplates:
    """Download an AmP species entry and wrap its files as ``EstimationTemplates``.

    The four species files are saved in ``folder/<species>/`` with everything else the entry needs to run: data
    files read by ``mydata`` or ``predict`` (which have no fixed names) and ``results_<species>.mat`` when available.
    Web pages and leftover ``.m`` files are left out. Each species file is wrapped verbatim in a ``CopyFileTemplate``, so the returned
    object can be used directly for a single-species estimation or as the starting point for adapting the files
    into substitution templates for a multitier workflow.

    Templates only cover the four species files. If they are rendered into another folder, copy the entry's data
    files there as well.

    @raise RuntimeError: if the entry cannot be listed or any of the four species files could not be downloaded.
    """
    client = AmPClient() if client is None else client
    try:
        listed_files = client.list_species_files(species, include_html=False)
    except requests.RequestException as error:
        raise RuntimeError(f"Could not list the AmP files of species '{species}': {error}") from error

    species_files = resolve_species_file_names(species, FILE_KEYS)
    # Other .m files in entries are leftovers (e.g. mydata_<species>_old.m); no entry calls them
    other_files = [file for file in listed_files if not file.lower().endswith(".m")]
    report = download_species(
        species,
        folder,
        files=dict.fromkeys([*species_files, *other_files]),
        overwrite=overwrite,
        check_update=check_update,
        client=client,
    )
    missing = {
        file_name: report.errors.get(file_name, "")
        for file_name in species_files
        if report.files.get(file_name) is DownloadStatus.FAILED
    }
    if missing:
        raise RuntimeError(f"Could not download the AmP files of species '{species}': {missing}")

    return EstimationTemplates(
        **{key: CopyFileTemplate(report.folder / file_name) for key, file_name in zip(FILE_KEYS, species_files)}
    )
