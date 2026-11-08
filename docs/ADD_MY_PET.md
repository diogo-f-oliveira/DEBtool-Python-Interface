# Add-my-Pet Integration

`DEBtoolPyIF.add_my_pet` fetches and reuses content from the [Add-my-Pet (AmP)](https://www.bio.vu.nl/thb/deb/deblab/add_my_pet/) collection. It only needs internet access: files are downloaded over HTTP and `.mat` files are read with SciPy, so no MATLAB session is required.

## Installation

`add_my_pet` needs a few extra packages (`requests`, `scipy`, `platformdirs` and `tqdm`) that the rest of DEBtoolPyIF does not use. Install them with the `amp` extra:

```console
pip install "DEBtoolPyIF[amp]"
```

Importing `DEBtoolPyIF.add_my_pet` without them raises an `ImportError` that names the missing package and this command.

## Where files go

Every function saves into a **folder**:

- **Pass a folder** to get the files somewhere you can see them, open them in MATLAB, edit them and keep them with your project. This is what most users want.

  ```python
  download_species("Danio_rerio", "my_project/amp")
  # my_project/amp/amp_manifest.csv
  # my_project/amp/Danio_rerio/mydata_Danio_rerio.m, pars_init_..., predict_..., run_..., results_...
  ```

- **Leave the folder out** to use a default folder, which suits scripts that only read the data through Python, such as machine-learning pipelines. `get_cache_dir()` returns it: the `DEBTOOLPYIF_AMP_CACHE` environment variable if set, otherwise your system's cache folder.

  | OS | Default folder |
  |---|---|
  | Windows | `%LOCALAPPDATA%\DEBtoolPyIF\Cache\add_my_pet` |
  | macOS | `~/Library/Caches/DEBtoolPyIF/add_my_pet` |
  | Linux | `~/.cache/DEBtoolPyIF/add_my_pet` |

Both work the same way. A folder of files you downloaded earlier can be used directly.

## Downloading species files

```python
from DEBtoolPyIF.add_my_pet import download_allstat, download_amp_collection, download_species

# All estimation files of one species into species/Bos_primigenius_Angus/
report = download_species("Bos_primigenius_Angus", "species")
print(report.amp_version)  # '20161116'
print(report.files)  # {file name: DownloadStatus}

# Only some files, using short keys (mydata, pars_init, predict, run, results) or file names
download_species("Danio_rerio", "species", files=("mydata", "results"))

# Many species in parallel (species=None downloads the whole collection)
reports = download_amp_collection("species", ["Danio_rerio", "Daphnia_magna"], check_update=True)
failed = {name: r.errors for name, r in reports.items() if not r.ok}

# The allStat.mat table of all species, without loading it
path = download_allstat("species")
```

Without `files=`, everything in the entry is downloaded except result figures. That includes the data files some entries read from `mydata` or `predict` (such as `tL.txt` or `LW.csv`), which have no fixed names. If you pass `files=`, only those files are downloaded, so an entry that reads data files will not run from them alone.

Existing files are kept by default. `check_update=True` replaces a local file only when the AmP copy is newer, and `overwrite=True` always replaces it. Downloaded files take the date AmP published them, so repeated `check_update` runs only transfer what changed. Download errors are collected in each `SpeciesDownloadReport` instead of being raised.

A file you edit gets a newer date than the AmP copy, so `check_update=True` will not replace it. Use `overwrite=True` to get the AmP version back.

### Large downloads

The AmP server can stop accepting connections after many requests, without any error message, and it can stay unreachable from your connection for hours. To avoid this, requests are sent 0.5 s apart, so downloading the whole collection takes several hours. `download_amp_collection` tells you what to expect at the start of a large download.

If the server stops responding, the download stops with a warning instead of failing species after species. Run the same command later to continue: files you already have are not downloaded again.

To go slower, pass your own client: `download_amp_collection("species", client=AmPClient(request_delay=2))`. Please be considerate of this shared server, and only download the species you need.

## Versions and the manifest

AmP identifies each version of an entry by its acceptance date: the current version of an entry is published as `entries_zip/<species>_<yyyymmdd>.zip`, and older versions are kept in `entries_archive/`. This package uses that same date as the **AmP version**.

Each folder has an `amp_manifest.csv`, which can be opened in Excel or read with `read_manifest()`:

| species | amp_version | files | downloaded_at | source_url |
|---|---|---|---|---|
| Danio_rerio | 20180809 | mydata_Danio_rerio.m;results_Danio_rerio.mat | 2026-11-06T10:15:02+00:00 | https://www.bio.vu.nl/.../entries/Danio_rerio/ |

Use `species` and `amp_version` to cite what you used. The version is read from `metaData.date_acc` in the `mydata` or `results` file, so it is blank if the folder has neither.

The `allStat` table has its own row. It has no acceptance date, so its version is the date AmP last published the file.

Close the manifest in Excel before downloading: Excel locks open files on Windows. The files still download, but the manifest is not updated and you get a warning.

## Fetching parameter sets

```python
from DEBtoolPyIF.add_my_pet import fetch_species_parameters, fetch_allstat, load_results_mat

results = fetch_species_parameters("Bos_primigenius_Angus", "species")
results.model        # 'stx'
results.amp_version  # '20161116'
results.par["p_M"]   # parameter values
results.to_frame()   # value, free, units and label per parameter
results.stats        # MRE, SMSE, ...

allstat = fetch_allstat("species")  # pandas DataFrame, one row per AmP species
allstat.loc[allstat["family"] == "Bovidae", ["model", "MRE", "p_M", "kap"]]

load_results_mat("path/to/results_my_species.mat")  # also works for your own estimation results
```

Each file is downloaded once and then reused. By default AmP is not contacted again, so rerunning a script gives the same parameters even if the entry was revised. Pass `check_update=True` to refresh. If AmP cannot be reached and a local file exists, it is used with a warning.

For published analyses, keep the folder with your project: the exact AmP files and their versions travel with the analysis.

## Clearing the default folder

`clear_cache("Danio_rerio")` deletes one species from the default folder, `clear_cache("allStat")` the `allStat` file, and `clear_cache()` everything. Only files listed in the manifest are deleted. Folders you chose yourself are never touched by `clear_cache`; delete those files directly.

## Bootstrapping a workflow

```python
from DEBtoolPyIF.add_my_pet import bootstrap_species

templates = bootstrap_species("Bos_primigenius_Angus", "workflows")
```

This downloads the four species files to `workflows/Bos_primigenius_Angus/`, along with any data files the entry reads and `results_<species>.mat` when available. Web pages and leftover `.m` files in the entry, such as `mydata_<species>_old.m`, are skipped. It returns an `EstimationTemplates` whose entries are verbatim `CopyFileTemplate`s, which you can use to rerun an AmP estimation.

These templates are copies, not editable templates. Turning an AmP entry into `MultitierMyDataSubstitutionTemplate` / `MultitierParsInitSubstitutionTemplate` sources is still done by hand. Templates also only cover the four species files: if you render them into another folder, copy the entry's data files there as well.

## Lower-level access

`AmPClient` exposes the HTTP layer (`list_species`, `list_species_files`, `download_species_file`, `download_ampdata_file`, `download_url`). Pass a shared client to the functions above to reuse its connection pool, or a custom `base_url` to target a mirror.
