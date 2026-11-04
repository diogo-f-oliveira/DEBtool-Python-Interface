"""Tools to fetch and reuse content from the Add-my-Pet (AmP) collection.

No MATLAB session is needed: files are downloaded over HTTP and ``.mat`` files are read with SciPy.
"""

from .bootstrap import bootstrap_species
from .cache import CacheRecord, clear_cache, get_cache_dir, read_cache_record
from .client import AmPClient, DownloadStatus, parse_directory_listing
from .download import (
    SPECIES_FILE_PATTERNS,
    SpeciesDownloadReport,
    download_amp_database,
    download_species,
)
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
    "CacheRecord",
    "DownloadStatus",
    "ENTRIES_URL",
    "ENTRIES_WEB_URL",
    "SPECIES_FILE_PATTERNS",
    "SpeciesDownloadReport",
    "bootstrap_species",
    "clear_cache",
    "download_amp_database",
    "download_species",
    "fetch_allstat",
    "fetch_species_parameters",
    "get_cache_dir",
    "load_allstat",
    "load_results_mat",
    "parse_directory_listing",
    "read_cache_record",
]
