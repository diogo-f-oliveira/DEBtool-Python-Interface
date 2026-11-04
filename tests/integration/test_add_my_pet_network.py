import pytest
import requests

from DEBtoolPyIF.add_my_pet import (
    AMP_BASE_URL,
    AmPClient,
    DownloadStatus,
    bootstrap_species,
    fetch_species_parameters,
    read_cache_record,
)

pytestmark = [pytest.mark.integration, pytest.mark.network]

SPECIES = "Bos_primigenius_Angus"


@pytest.fixture(scope="module", autouse=True)
def require_amp_website():
    try:
        requests.head(f"{AMP_BASE_URL}/entries/{SPECIES}/", timeout=10).raise_for_status()
    except requests.RequestException as error:
        pytest.skip(f"Add-my-Pet website is not reachable: {error}")


def test_bootstrap_and_fetch_parameters_from_amp(tmp_path):
    templates = bootstrap_species(SPECIES, tmp_path / "workflow")
    assert f"mydata_{SPECIES}" in templates.mydata.get_source()

    results = fetch_species_parameters(SPECIES, tmp_path / "cache")
    assert results.species == SPECIES
    assert results.model
    assert {"p_M", "kap", "v"} <= set(results.par)

    cached = tmp_path / "cache" / SPECIES / f"results_{SPECIES}.mat"
    record = read_cache_record(cached)
    assert record.etag and record.last_modified

    # An update check finds the cached file up to date, by ETag in the cache and by date for plain downloads
    fetch_species_parameters(SPECIES, tmp_path / "cache", check_update=True)
    assert read_cache_record(cached) == record
    status = AmPClient().download_species_file(SPECIES, cached.name, cached.parent, check_update=True)
    assert status is DownloadStatus.NOT_MODIFIED
