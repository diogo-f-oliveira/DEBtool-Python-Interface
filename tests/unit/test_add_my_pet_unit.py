import os
from email.utils import parsedate_to_datetime

import numpy as np
import pytest
import requests
import scipy.io

from DEBtoolPyIF.add_my_pet import (
    AmPClient,
    DownloadStatus,
    MANIFEST_FILE_NAME,
    bootstrap_species,
    clear_cache,
    download_amp_database,
    download_species,
    fetch_species_parameters,
    get_cache_dir,
    load_allstat,
    load_results_mat,
    parse_directory_listing,
    read_amp_version,
    read_manifest,
)
from DEBtoolPyIF.add_my_pet.manifest import ManifestEntry, update_manifest
from DEBtoolPyIF.estimation_files.templates import CopyFileTemplate

BASE_URL = "https://amp.test/add_my_pet"
SPECIES = "Bos_test"
LAST_MODIFIED = "Thu, 15 Dec 2022 11:40:33 GMT"

LISTING_HTML = """
<html><body><table>
<tr><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a></th></tr>
<tr><td><a href="/thb/deb/deblab/add_my_pet/entries/">Parent Directory</a></td></tr>
<tr><td><a href="mydata_Bos_test.m">mydata_Bos_test.m</a></td></tr>
<tr><td><a href="pars_init_Bos_test.m">pars_init_Bos_test.m</a></td></tr>
<tr><td><a href="predict_Bos_test.m">predict_Bos_test.m</a></td></tr>
<tr><td><a href="run_Bos_test.m">run_Bos_test.m</a></td></tr>
<tr><td><a href="results_Bos_test.mat">results_Bos_test.mat</a></td></tr>
<tr><td><a href="results_Bos_test_01.png">results_Bos_test_01.png</a></td></tr>
<tr><td><a href="figs/">figs/</a></td></tr>
<tr><td><a href="https://elsewhere.test/page.html">external</a></td></tr>
</table></body></html>
"""


class FakeResponse:
    def __init__(self, url, status_code=200, body=b"", headers=None, stream_error=None):
        self.url = url
        self.status_code = status_code
        self.content = body
        self.text = body.decode("utf-8", errors="replace")
        self.headers = headers or {}
        self.stream_error = stream_error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} for {self.url}")

    def iter_content(self, chunk_size=1):
        yield self.content[:1]
        if self.stream_error is not None:
            raise self.stream_error
        yield self.content[1:]

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class FakeSession:
    """Serves registered URLs; unknown URLs return 404. Honors If-Modified-Since against ``last_modified``."""

    def __init__(self, routes=None):
        self.routes = dict(routes or {})
        self.requests = []
        self.last_modified = LAST_MODIFIED

    def get(self, url, headers=None, stream=False, timeout=None):
        headers = headers or {}
        self.requests.append((url, headers))
        route = self.routes.get(url)
        if route is None:
            return FakeResponse(url, status_code=404)
        if isinstance(route, Exception):
            raise route
        if isinstance(route, FakeResponse):
            return route
        since = headers.get("If-Modified-Since")
        if since and parsedate_to_datetime(since) >= parsedate_to_datetime(self.last_modified):
            return FakeResponse(url, status_code=304)
        return FakeResponse(url, body=route, headers={"Last-Modified": self.last_modified})


def species_url(file_name=""):
    return f"{BASE_URL}/entries/{SPECIES}/{file_name}"


def species_routes():
    routes = {species_url(): LISTING_HTML.encode("utf-8")}
    for kind in ("mydata", "pars_init", "predict", "run"):
        routes[species_url(f"{kind}_{SPECIES}.m")] = f"function {kind}_{SPECIES}\n".encode("utf-8")
    routes[species_url(f"results_{SPECIES}.mat")] = b"mat-bytes"
    return routes


def make_client(routes):
    return AmPClient(base_url=BASE_URL, session=FakeSession(routes))


def test_parse_directory_listing_keeps_only_relative_entries():
    assert parse_directory_listing(LISTING_HTML, include_dirs=False) == [
        "mydata_Bos_test.m",
        "pars_init_Bos_test.m",
        "predict_Bos_test.m",
        "run_Bos_test.m",
        "results_Bos_test.mat",
        "results_Bos_test_01.png",
    ]
    assert parse_directory_listing(LISTING_HTML, include_files=False) == ["figs/"]


def test_list_species_files_skips_result_figures_but_keeps_results_mat():
    client = make_client(species_routes())

    assert client.list_species_files(SPECIES) == [
        f"mydata_{SPECIES}.m",
        f"pars_init_{SPECIES}.m",
        f"predict_{SPECIES}.m",
        f"run_{SPECIES}.m",
        f"results_{SPECIES}.mat",
    ]
    assert f"results_{SPECIES}.mat" not in client.list_species_files(SPECIES, include_results_mat=False)


def test_download_skips_existing_files_and_checks_updates_with_conditional_get(tmp_path):
    client = make_client(species_routes())
    file_name = f"mydata_{SPECIES}.m"
    local_path = tmp_path / file_name

    assert client.download_species_file(SPECIES, file_name, tmp_path) is DownloadStatus.DOWNLOADED
    # The local file takes the remote modification time
    assert local_path.stat().st_mtime == parsedate_to_datetime(LAST_MODIFIED).timestamp()

    assert client.download_species_file(SPECIES, file_name, tmp_path) is DownloadStatus.SKIPPED_EXISTS

    local_path.write_text("local edits")
    os.utime(local_path, (parsedate_to_datetime(LAST_MODIFIED).timestamp(),) * 2)
    status = client.download_species_file(SPECIES, file_name, tmp_path, check_update=True)
    assert status is DownloadStatus.NOT_MODIFIED
    assert local_path.read_text() == "local edits"
    assert client.session.requests[-1][1]["If-Modified-Since"] == LAST_MODIFIED

    os.utime(local_path, (0, 0))
    assert client.download_species_file(SPECIES, file_name, tmp_path, check_update=True) is DownloadStatus.UPDATED
    assert local_path.read_text() == f"function mydata_{SPECIES}\n"

    local_path.write_text("local edits")
    assert client.download_species_file(SPECIES, file_name, tmp_path, overwrite=True) is DownloadStatus.UPDATED
    assert local_path.read_text() == f"function mydata_{SPECIES}\n"


def test_interrupted_download_keeps_existing_file_and_leaves_no_partial_file(tmp_path):
    file_name = f"mydata_{SPECIES}.m"
    routes = species_routes()
    routes[species_url(file_name)] = FakeResponse(
        species_url(file_name), body=b"new content", stream_error=requests.ConnectionError("connection dropped"),
    )
    client = make_client(routes)
    (tmp_path / file_name).write_text("old content")

    with pytest.raises(requests.ConnectionError):
        client.download_species_file(SPECIES, file_name, tmp_path, overwrite=True)

    assert (tmp_path / file_name).read_text() == "old content"
    assert sorted(path.name for path in tmp_path.iterdir()) == [file_name]


def test_download_species_records_failures_without_raising(tmp_path):
    routes = species_routes()
    del routes[species_url(f"predict_{SPECIES}.m")]
    client = make_client(routes)

    report = download_species(SPECIES, tmp_path, client=client)

    assert not report.ok
    assert report.files[f"predict_{SPECIES}.m"] is DownloadStatus.FAILED
    assert set(report.errors) == {f"predict_{SPECIES}.m"}
    assert report.files[f"mydata_{SPECIES}.m"] is DownloadStatus.DOWNLOADED
    assert set(report.paths()) == {
        f"mydata_{SPECIES}.m", f"pars_init_{SPECIES}.m", f"run_{SPECIES}.m", f"results_{SPECIES}.mat",
    }
    assert (tmp_path / SPECIES / f"run_{SPECIES}.m").exists()

    listing_report = download_species("Missing_species", tmp_path, client=client)
    assert listing_report.listing_error is not None
    assert listing_report.files == {}


def test_download_species_expands_short_file_keys(tmp_path):
    client = make_client(species_routes())

    report = download_species(SPECIES, tmp_path, files=("mydata", "results", f"run_{SPECIES}.m"), client=client)

    assert list(report.files) == [f"mydata_{SPECIES}.m", f"results_{SPECIES}.mat", f"run_{SPECIES}.m"]
    assert report.ok


def write_results_mat(path, z=55.5, date_acc=(2020, 1, 2)):
    scipy.io.savemat(path, {
        "par": {"z": z, "kap": 0.95, "T_A": 8000, "free": {"z": 1, "kap": 1, "T_A": 0}},
        "metaPar": {"model": "stx", "MRE": 0.08, "SMSE": 0.01},
        "txtPar": {
            "units": {"z": "-", "kap": "-", "T_A": "K"},
            "label": {"z": "zoom factor", "kap": "allocation fraction to soma", "T_A": "Arrhenius temperature"},
        },
        "metaData": {"species": SPECIES, "COMPLETE": 2.5, "date_acc": np.array(date_acc)},
    })


def test_load_results_mat_reads_parameters_metadata_and_statistics(tmp_path):
    path = tmp_path / f"results_{SPECIES}.mat"
    write_results_mat(path)

    results = load_results_mat(path)

    assert results.species == SPECIES
    assert results.model == "stx"
    assert results.par == {"z": 55.5, "kap": 0.95, "T_A": 8000.0}
    assert results.free == {"z": 1, "kap": 1, "T_A": 0}
    assert results.units["T_A"] == "K"
    assert results.labels["kap"] == "allocation fraction to soma"
    assert results.stats == {"MRE": 0.08, "SMSE": 0.01}
    table = results.to_frame()
    assert list(table.columns) == ["value", "free", "units", "label"]
    assert table.loc["T_A", "value"] == 8000.0


def test_load_allstat_builds_one_row_per_species(tmp_path):
    path = tmp_path / "allStat.mat"
    scipy.io.savemat(path, {"allStat": {
        "Sp_a": {
            "species_en": "species a", "family": "Fa", "order": "Oa", "class": "Ca", "phylum": "Pa",
            "id_CoL": "X1", "model": "std", "MRE": 0.1, "SMSE": 0.2, "COMPLETE": 2.5,
            "date_acc": np.array([2020, 1, 2]), "date_subm": np.array([2019, 12, 31]),
            "p_M": 30.0, "author": np.array(["Someone", "Other"], dtype=object),
        },
        "Sp_b": {
            "species_en": "species b", "family": "Fb", "order": "Ob", "class": "Cb", "phylum": "Pb",
            "id_CoL": "X2", "model": "abj", "MRE": 0.3, "SMSE": 0.4, "COMPLETE": 3.0,
            "date_acc": np.array([2021, 5, 6]), "date_subm": np.array([2021, 4, 1]), "s_M": 2.0,
        },
    }})

    table = load_allstat(path)

    assert list(table.index) == ["Sp_a", "Sp_b"]
    assert table.loc["Sp_a", "family"] == "Fa"
    assert table.loc["Sp_b", "model"] == "abj"
    assert table.loc["Sp_a", "completeness"] == 2.5
    assert table.loc["Sp_a", "date_update"] == "2020-01-02"
    assert table.loc["Sp_b", "date_submission"] == "2021-04-01"
    assert table.loc["Sp_a", "p_M"] == 30.0
    assert np.isnan(table.loc["Sp_b", "p_M"])
    assert table.loc["Sp_b", "s_M"] == 2.0
    assert "author" not in table.columns


def results_mat_bytes(tmp_path, **kwargs):
    path = tmp_path / "source.mat"
    write_results_mat(path, **kwargs)
    return path.read_bytes()


def test_download_species_records_version_and_files_in_a_readable_manifest(tmp_path):
    routes = species_routes()
    routes[species_url(f"mydata_{SPECIES}.m")] = b"metaData.date_acc    = [2016 11 16]; \n"
    client = make_client(routes)

    report = download_species(SPECIES, tmp_path, files=("mydata", "predict"), client=client)

    assert report.amp_version == "20161116"
    row = read_manifest(tmp_path).set_index("species").loc[SPECIES]
    assert row["amp_version"] == "20161116"
    assert row["files"] == f"mydata_{SPECIES}.m;predict_{SPECIES}.m"
    assert row["source_url"] == species_url()
    assert row["downloaded_at"]
    # The folder only holds the species files and the manifest
    assert sorted(path.name for path in tmp_path.iterdir()) == [SPECIES, MANIFEST_FILE_NAME]
    assert sorted(path.name for path in (tmp_path / SPECIES).iterdir()) == [
        f"mydata_{SPECIES}.m", f"predict_{SPECIES}.m",
    ]

    # Adding files keeps the row, and a run that transfers nothing keeps the download time
    download_species(SPECIES, tmp_path, files=("run",), client=client)
    row = read_manifest(tmp_path).set_index("species").loc[SPECIES]
    assert row["files"] == f"mydata_{SPECIES}.m;predict_{SPECIES}.m;run_{SPECIES}.m"
    downloaded_at = row["downloaded_at"]
    download_species(SPECIES, tmp_path, files=("run",), client=client)
    assert read_manifest(tmp_path).set_index("species").loc[SPECIES, "downloaded_at"] == downloaded_at


def test_download_species_does_not_add_failed_species_to_the_manifest(tmp_path):
    client = make_client(species_routes())

    download_species("Missing_species", tmp_path, client=client)

    assert read_manifest(tmp_path).empty


def test_download_amp_database_records_all_species_in_one_manifest(tmp_path):
    routes = species_routes()
    routes[f"{BASE_URL}/entries/Other_species/mydata_Other_species.m"] = b"metaData.date_acc = [2020 01 02];\n"
    client = make_client(routes)

    reports = download_amp_database(
        tmp_path, [SPECIES, "Other_species", "Missing_species"], files=("mydata",), progress=False, client=client,
    )

    assert list(reports) == [SPECIES, "Other_species", "Missing_species"]
    assert not reports["Missing_species"].ok
    manifest = read_manifest(tmp_path).set_index("species")
    assert list(manifest.index) == [SPECIES, "Other_species"]
    assert manifest.loc["Other_species", "amp_version"] == "20200102"


def test_read_amp_version_uses_most_recent_of_mydata_and_results(tmp_path):
    assert read_amp_version(tmp_path, SPECIES) is None

    write_results_mat(tmp_path / f"results_{SPECIES}.mat")
    assert read_amp_version(tmp_path, SPECIES) == "20200102"

    mydata = tmp_path / f"mydata_{SPECIES}.m"
    mydata.write_text("% metaData.date_acc = [1999 01 01];\nmetaData.date_acc    = [2021 3 9];\n")
    assert read_amp_version(tmp_path, SPECIES) == "20210309"

    mydata.write_text("metaData.date_acc = [2019 01 01];\n")
    assert read_amp_version(tmp_path, SPECIES) == "20200102"


def test_fetch_species_parameters_reuses_local_file_unless_asked_to_check_updates(tmp_path):
    url = species_url(f"results_{SPECIES}.mat")
    client = make_client({url: results_mat_bytes(tmp_path)})
    folder = tmp_path / "project"

    results = fetch_species_parameters(SPECIES, folder, client=client)
    assert results.par["z"] == 55.5
    assert results.amp_version == "20200102"
    assert read_manifest(folder).set_index("species").loc[SPECIES, "amp_version"] == "20200102"

    # Default: the local file is reused without downloading, even if AmP changed
    client.session.routes[url] = results_mat_bytes(tmp_path, z=60.0, date_acc=[2024, 5, 6])
    client.session.last_modified = "Wed, 15 May 2024 10:00:00 GMT"
    assert fetch_species_parameters(SPECIES, folder, client=client).par["z"] == 55.5

    assert fetch_species_parameters(SPECIES, folder, client=client, check_update=True).par["z"] == 60.0
    assert read_manifest(folder).set_index("species").loc[SPECIES, "amp_version"] == "20240506"


def test_fetch_species_parameters_uses_local_file_when_amp_is_unreachable(tmp_path):
    url = species_url(f"results_{SPECIES}.mat")
    client = make_client({url: results_mat_bytes(tmp_path)})
    fetch_species_parameters(SPECIES, tmp_path, client=client)
    client.session.routes[url] = requests.ConnectionError("offline")

    with pytest.warns(UserWarning, match="local copy"):
        results = fetch_species_parameters(SPECIES, tmp_path, client=client, check_update=True)
    assert results.par["z"] == 55.5

    with pytest.raises(RuntimeError, match="offline"):
        fetch_species_parameters(SPECIES, tmp_path / "empty", client=client)


def test_functions_use_the_default_folder_when_none_is_given(tmp_path, monkeypatch):
    monkeypatch.setenv("DEBTOOLPYIF_AMP_CACHE", str(tmp_path / "from_env"))
    client = make_client({species_url(f"results_{SPECIES}.mat"): results_mat_bytes(tmp_path)})

    fetch_species_parameters(SPECIES, client=client)

    assert (tmp_path / "from_env" / SPECIES / f"results_{SPECIES}.mat").exists()
    assert list(read_manifest()["species"]) == [SPECIES]


def test_get_cache_dir_uses_environment_variable_or_os_cache_folder(tmp_path, monkeypatch):
    monkeypatch.delenv("DEBTOOLPYIF_AMP_CACHE", raising=False)
    assert get_cache_dir().parts[-1] == "add_my_pet"
    assert "DEBtoolPyIF" in get_cache_dir().parts

    monkeypatch.setenv("DEBTOOLPYIF_AMP_CACHE", str(tmp_path / "from_env"))
    assert get_cache_dir() == tmp_path / "from_env"


def test_clear_cache_removes_only_files_listed_in_the_manifest(tmp_path, monkeypatch):
    folder = tmp_path / "cache"
    monkeypatch.setenv("DEBTOOLPYIF_AMP_CACHE", str(folder))
    client = make_client(species_routes())
    download_species(SPECIES, files=("mydata", "run"), client=client)
    notes = folder / "Other_species" / "my_notes.txt"
    notes.parent.mkdir()
    notes.write_text("not from AmP")
    (folder / SPECIES / "my_analysis.m").write_text("% my own file")

    removed = clear_cache(SPECIES)

    assert sorted(path.name for path in removed) == [f"mydata_{SPECIES}.m", f"run_{SPECIES}.m"]
    assert (folder / SPECIES / "my_analysis.m").exists()
    assert notes.exists()
    assert not (folder / MANIFEST_FILE_NAME).exists()
    assert clear_cache() == []


def test_manifest_open_in_another_program_warns_instead_of_failing(tmp_path, monkeypatch):
    def locked_replace(source, destination):
        raise PermissionError("file is open")

    monkeypatch.setattr("DEBtoolPyIF.add_my_pet.manifest.os.replace", locked_replace)
    entry = ManifestEntry(species=SPECIES, files=("a.m",), source_url=species_url())

    with pytest.warns(UserWarning, match="Close it"):
        update_manifest(tmp_path, [entry])

    assert list(tmp_path.iterdir()) == []


def test_bootstrap_species_returns_copy_file_templates(tmp_path):
    client = make_client(species_routes())

    templates = bootstrap_species(SPECIES, tmp_path, client=client)

    for kind in ("mydata", "pars_init", "predict", "run"):
        template = getattr(templates, kind)
        assert isinstance(template, CopyFileTemplate)
        assert template.get_source() == f"function {kind}_{SPECIES}\n"
    assert (tmp_path / SPECIES / f"results_{SPECIES}.mat").exists()


def test_bootstrap_species_tolerates_missing_results_but_not_missing_species_files(tmp_path):
    routes = species_routes()
    del routes[species_url(f"results_{SPECIES}.mat")]
    bootstrap_species(SPECIES, tmp_path / "no_results", client=make_client(routes))

    del routes[species_url(f"predict_{SPECIES}.m")]
    with pytest.raises(RuntimeError, match=f"predict_{SPECIES}.m"):
        bootstrap_species(SPECIES, tmp_path / "no_predict", client=make_client(routes))
