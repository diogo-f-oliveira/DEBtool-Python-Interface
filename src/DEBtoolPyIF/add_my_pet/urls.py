"""URLs of the Add-my-Pet (AmP) collection."""

from __future__ import annotations

AMP_BASE_URL = "https://www.bio.vu.nl/thb/deb/deblab/add_my_pet"
ENTRIES_URL = f"{AMP_BASE_URL}/entries"
ENTRIES_WEB_URL = f"{AMP_BASE_URL}/entries_web"
AMPDATA_URL = f"{AMP_BASE_URL}/AmPdata"


def species_dir_url(species: str, base_url: str = AMP_BASE_URL) -> str:
    return f"{base_url}/entries/{species}/"


def species_file_url(species: str, file_name: str, base_url: str = AMP_BASE_URL) -> str:
    return f"{base_url}/entries/{species}/{file_name}"


def ampdata_file_url(file_name: str, base_url: str = AMP_BASE_URL) -> str:
    return f"{base_url}/AmPdata/{file_name}"
