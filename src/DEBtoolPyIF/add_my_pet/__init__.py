"""Tools to fetch and reuse content from the Add-my-Pet (AmP) collection.

No MATLAB session is needed: files are downloaded over HTTP and ``.mat`` files are read with SciPy. Files are saved in
a folder of your choice, or in a default folder when none is given, and each folder's ``amp_manifest.csv`` records the
AmP version of every species it contains.
"""

from .bootstrap import bootstrap_species
from .client import AmPClient, DownloadStatus, parse_directory_listing
from .download import (
    SPECIES_FILE_PATTERNS,
    SpeciesDownloadReport,
    download_amp_collection,
    download_species,
)
from .manifest import MANIFEST_FILE_NAME, clear_cache, get_cache_dir, read_amp_version, read_manifest
from .parameters import (
    AmPResults,
    fetch_allstat,
    fetch_species_parameters,
    load_allstat,
    load_results_mat,
)
from .urls import AMP_BASE_URL, AMPDATA_URL, ENTRIES_URL, ENTRIES_WEB_URL

__all__ = [
    "AMP_BASE_URL",
    "AMPDATA_URL",
    "AmPClient",
    "AmPResults",
    "DownloadStatus",
    "ENTRIES_URL",
    "ENTRIES_WEB_URL",
    "MANIFEST_FILE_NAME",
    "SPECIES_FILE_PATTERNS",
    "SpeciesDownloadReport",
    "bootstrap_species",
    "clear_cache",
    "download_amp_collection",
    "download_species",
    "fetch_allstat",
    "fetch_species_parameters",
    "get_cache_dir",
    "load_allstat",
    "load_results_mat",
    "parse_directory_listing",
    "read_amp_version",
    "read_manifest",
]
