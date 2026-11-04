# Add-my-Pet Integration

`DEBtoolPyIF.add_my_pet` fetches and reuses content from the [Add-my-Pet (AmP)](https://www.bio.vu.nl/thb/deb/deblab/add_my_pet/) collection. It only needs internet access: files are downloaded over HTTP and `.mat` files are read with SciPy, so no MATLAB session is required.

## Downloading species files

```python
from DEBtoolPyIF.add_my_pet import download_species, download_amp_database

# All estimation files of one species into species/Bos_primigenius_Angus/
report = download_species("Bos_primigenius_Angus", "species")
print(report.files)  # {file name: DownloadStatus}

# Only some files, using short keys (mydata, pars_init, predict, run, results) or file names
download_species("Danio_rerio", "species", files=("mydata", "results"))

# Many species in parallel (species=None downloads the whole collection)
reports = download_amp_database("species", ["Danio_rerio", "Daphnia_magna"], check_update=True)
failed = {name: r.errors for name, r in reports.items() if not r.ok}
```

Existing files are kept by default. `check_update=True` replaces a local file only when the AmP version is newer (conditional GET), and `overwrite=True` always replaces it. Downloaded files take the AmP modification time, so repeated `check_update` runs only transfer changed files. Download errors are collected in each `SpeciesDownloadReport` instead of being raised.

## Fetching parameter sets

```python
from DEBtoolPyIF.add_my_pet import fetch_species_parameters, fetch_allstat, load_results_mat

results = fetch_species_parameters("Bos_primigenius_Angus")                     # cached after the first call
results = fetch_species_parameters("Bos_primigenius_Angus", check_update=True)  # refresh if AmP changed
results.model        # 'stx'
results.par["p_M"]   # parameter values
results.to_frame()   # value, free, units and label per parameter
results.stats        # MRE, SMSE, ...

allstat = fetch_allstat()  # pandas DataFrame, one row per AmP species
allstat.loc[allstat["family"] == "Bovidae", ["model", "MRE", "p_M", "kap"]]

load_results_mat("path/to/results_my_species.mat")  # also works for your own estimation results
```

## The cache

`fetch_species_parameters` and `fetch_allstat` download each file once and keep it in a local cache. The other download functions save into the folder you choose and do not use the cache.

**Location.** `get_cache_dir()` returns the folder in use: the `cache_dir` argument if given, otherwise the `DEBTOOLPYIF_AMP_CACHE` environment variable, otherwise the operating system's user cache folder:

| OS | Default cache folder |
|---|---|
| Windows | `%LOCALAPPDATA%\DEBtoolPyIF\Cache\add_my_pet` |
| macOS | `~/Library/Caches/DEBtoolPyIF/add_my_pet` |
| Linux | `~/.cache/DEBtoolPyIF/add_my_pet` (or `$XDG_CACHE_HOME`) |

Files are stored as `<cache>/<species>/results_<species>.mat` and `<cache>/allStat.mat`, each with a small `<file>.amp.json` sidecar recording the source URL, the server's `ETag` and `Last-Modified` values, a SHA-256 hash of the content and the download time (see `read_cache_record`).

**Updates.** By default a cached file is reused without contacting AmP, so rerunning a script returns the same parameters even if the AmP entry was revised in the meantime. Pass `check_update=True` to ask AmP whether the file changed: the stored `ETag` is sent back to the server, which replies "not modified" (nothing is transferred) or sends the new version. If AmP cannot be reached, the cached copy is used with a warning.

**Integrity.** A cached file whose content no longer matches its recorded hash (for example, edited by hand) is downloaded again with a warning. Treat the cache as read-only; copy files elsewhere to modify them.

**Reproducibility.** For published analyses, fetch once and keep the default `check_update=False`, or pass a `cache_dir` inside the project so the exact AmP files travel with the analysis.

**Clearing.** `clear_cache("Danio_rerio")` deletes one species, `clear_cache()` the whole cache. Only files with a `.amp.json` sidecar are deleted, so other files in the folder are never touched.

## Bootstrapping a workflow

```python
from DEBtoolPyIF.add_my_pet import bootstrap_species

templates = bootstrap_species("Bos_primigenius_Angus", "workflows")
```

This downloads the four species files (and `results_<species>.mat` when available) to `workflows/Bos_primigenius_Angus/` and returns an `EstimationTemplates` whose entries are verbatim `CopyFileTemplate`s. Use it to rerun an AmP estimation, or as the starting point for turning the files into `MultitierMyDataSubstitutionTemplate` / `MultitierParsInitSubstitutionTemplate` sources for a multitier workflow.

## Lower-level access

`AmPClient` exposes the HTTP layer (`list_species`, `list_species_files`, `download_species_file`, `download_ampdata_file`, `download_url`). Pass a shared client to the functions above to reuse its connection pool, or a custom `base_url` to target a mirror.
