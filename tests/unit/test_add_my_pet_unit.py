import os
from email.utils import parsedate_to_datetime

import numpy as np
import pytest
import requests
import scipy.io

from DEBtoolPyIF.add_my_pet import (
    AmPClient,
    DownloadStatus,
    bootstrap_species,
    clear_cache,
    download_species,
    fetch_species_parameters,
    get_cache_dir,
    load_allstat,
    load_results_mat,
    parse_directory_listing,
    read_cache_record,
)
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
    """Serves registered URLs; unknown URLs return 404.

    Honors If-None-Match against ``etag`` and, without it, If-Modified-Since against LAST_MODIFIED.
    """

    def __init__(self, routes=None):
        self.routes = dict(routes or {})
        self.requests = []
        self.etag = '"v1"'

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
        if "If-None-Match" in headers:
            if headers["If-None-Match"] == self.etag:
                return FakeResponse(url, status_code=304)
        else:
            since = headers.get("If-Modified-Since")
            if since and parsedate_to_datetime(since) >= parsedate_to_datetime(LAST_MODIFIED):
                return FakeResponse(url, status_code=304)
        return FakeResponse(url, body=route, headers={"Last-Modified": LAST_MODIFIED, "ETag": self.etag})


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


def write_results_mat(path, z=55.5):
    scipy.io.savemat(path, {
        "par": {"z": z, "kap": 0.95, "T_A": 8000, "free": {"z": 1, "kap": 1, "T_A": 0}},
        "metaPar": {"model": "stx", "MRE": 0.08, "SMSE": 0.01},
        "txtPar": {
            "units": {"z": "-", "kap": "-", "T_A": "K"},
            "label": {"z": "zoom factor", "kap": "allocation fraction to soma", "T_A": "Arrhenius temperature"},
        },
        "metaData": {"species": SPECIES, "COMPLETE": 2.5},
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


def results_mat_bytes(tmp_path, **par):
    path = tmp_path / "source.mat"
    write_results_mat(path, **par)
    return path.read_bytes()


def test_fetch_species_parameters_reuses_cache_and_revalidates_with_etag_on_request(tmp_path):
    url = species_url(f"results_{SPECIES}.mat")
    client = make_client({url: results_mat_bytes(tmp_path)})
    cache_dir = tmp_path / "cache"
    cached = cache_dir / SPECIES / f"results_{SPECIES}.mat"

    assert fetch_species_parameters(SPECIES, cache_dir, client=client).par["z"] == 55.5
    record = read_cache_record(cached)
    assert (record.url, record.etag, record.last_modified) == (url, '"v1"', LAST_MODIFIED)

    # Default: cached copy is reused without contacting AmP, even if AmP changed
    client.session.routes[url] = results_mat_bytes(tmp_path, z=60.0)
    client.session.etag = '"v2"'
    n_requests = len(client.session.requests)
    assert fetch_species_parameters(SPECIES, cache_dir, client=client).par["z"] == 55.5
    assert len(client.session.requests) == n_requests

    # check_update: conditional GET with the stored ETag picks up the new version
    assert fetch_species_parameters(SPECIES, cache_dir, client=client, check_update=True).par["z"] == 60.0
    assert client.session.requests[-1][1]["If-None-Match"] == '"v1"'
    assert read_cache_record(cached).etag == '"v2"'

    fetch_species_parameters(SPECIES, cache_dir, client=client, check_update=True)
    assert client.session.requests[-1][1]["If-None-Match"] == '"v2"'
    assert read_cache_record(cached).etag == '"v2"'


def test_fetch_species_parameters_redownloads_cached_files_edited_locally(tmp_path):
    url = species_url(f"results_{SPECIES}.mat")
    client = make_client({url: results_mat_bytes(tmp_path)})
    cache_dir = tmp_path / "cache"
    fetch_species_parameters(SPECIES, cache_dir, client=client)

    write_results_mat(cache_dir / SPECIES / f"results_{SPECIES}.mat", z=1.0)

    with pytest.warns(UserWarning, match="modified after download"):
        results = fetch_species_parameters(SPECIES, cache_dir, client=client)
    assert results.par["z"] == 55.5


def test_fetch_species_parameters_falls_back_to_cache_when_offline(tmp_path):
    url = species_url(f"results_{SPECIES}.mat")
    client = make_client({url: results_mat_bytes(tmp_path)})
    fetch_species_parameters(SPECIES, tmp_path, client=client)
    client.session.routes[url] = requests.ConnectionError("offline")

    with pytest.warns(UserWarning, match="cached copy"):
        results = fetch_species_parameters(SPECIES, tmp_path, client=client, check_update=True)
    assert results.par["z"] == 55.5

    with pytest.raises(requests.ConnectionError):
        fetch_species_parameters(SPECIES, tmp_path / "empty_cache", client=client)


def test_get_cache_dir_precedence(tmp_path, monkeypatch):
    monkeypatch.delenv("DEBTOOLPYIF_AMP_CACHE", raising=False)
    assert get_cache_dir().parts[-1] == "add_my_pet"
    assert "DEBtoolPyIF" in get_cache_dir().parts

    monkeypatch.setenv("DEBTOOLPYIF_AMP_CACHE", str(tmp_path / "from_env"))
    assert get_cache_dir() == tmp_path / "from_env"
    assert get_cache_dir(tmp_path / "explicit") == tmp_path / "explicit"


def test_clear_cache_removes_only_files_written_by_the_cache(tmp_path):
    url = species_url(f"results_{SPECIES}.mat")
    client = make_client({url: results_mat_bytes(tmp_path)})
    cache_dir = tmp_path / "cache"
    fetch_species_parameters(SPECIES, cache_dir, client=client)
    other_species = cache_dir / "Other_species"
    other_species.mkdir()
    (other_species / "my_notes.txt").write_text("not from AmP")

    removed = clear_cache(SPECIES, cache_dir=cache_dir)

    assert removed == [cache_dir / SPECIES / f"results_{SPECIES}.mat"]
    assert not (cache_dir / SPECIES).exists()
    assert clear_cache(cache_dir=cache_dir) == []
    assert (other_species / "my_notes.txt").exists()


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
