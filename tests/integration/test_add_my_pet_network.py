import pytest
import requests

from DEBtoolPyIF.add_my_pet import (
    AMP_BASE_URL,
    AmPClient,
    DownloadStatus,
    bootstrap_species,
    fetch_species_parameters,
    read_manifest,
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
    workflow = tmp_path / "workflow"
    templates = bootstrap_species(SPECIES, workflow)
    assert f"mydata_{SPECIES}" in templates.mydata.get_source()

    results = fetch_species_parameters(SPECIES, tmp_path / "parameters")
    assert results.species == SPECIES
    assert results.model
    assert {"p_M", "kap", "v"} <= set(results.par)

    # The version in the manifest is the date AmP uses to name the entry's zip file
    version = read_manifest(workflow).set_index("species").loc[SPECIES, "amp_version"]
    assert version == results.amp_version
    client = AmPClient()
    zip_files = client.list_directory(f"{AMP_BASE_URL}/entries_zip/", include_dirs=False)
    assert f"{SPECIES}_{version}.zip" in zip_files

    # An update check finds the local file up to date
    status = client.download_species_file(
        SPECIES, f"results_{SPECIES}.mat", tmp_path / "parameters" / SPECIES, check_update=True,
    )
    assert status is DownloadStatus.NOT_MODIFIED
