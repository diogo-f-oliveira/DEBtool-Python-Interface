# DEBtool-Python-Interface

`DEBtoolPyIF` is a Python interface to the MATLAB package DEBtool for Dynamic Energy Budget (DEB) model parameter estimation.

Its most mature current capability is multitier DEB parameter estimation across hierarchical levels, allowing parameters to be estimated from broader tiers down to more specific tiers.

The package also provides template-based generation of DEBtool species files (`mydata`, `pars_init`, `predict`, `run`) that support these workflows while preserving DEBtool naming and structure conventions. Broader AmP/species estimation support is still under development for future versions.

The experimental `add_my_pet` subpackage downloads entries and parameter sets from the [Add-my-Pet](https://www.bio.vu.nl/thb/deb/deblab/add_my_pet/) collection, without MATLAB.

## Learn More

The multitier workflow estimates DEB parameters sequentially across a hierarchy, from broader tiers to more specific ones. In practice, this lets users combine information from higher-level groups with more specific subgroup or individual data, so lower-tier fits start from a stable baseline instead of estimating every parameter from scratch.

This approach is useful when individual-level datasets are too sparse to support full parameter estimation on their own, but higher-level data can help anchor the fit. Typical use cases include estimating parameters across levels such as breed, treatment, population, pen, or individual, while controlling which parameters are re-estimated at each tier.


You can find more details on the multitier workflow and its implementation in [`docs/parameter_estimation/`](docs/parameter_estimation/). The [`README.md`](docs/parameter_estimation/README.md) inside provides a description of what each document covers and how they relate to each other.
For a compact map of the source tree and module responsibilities, see [`docs/PACKAGE_STRUCTURE.md`](docs/PACKAGE_STRUCTURE.md).
For a concrete example of a multitier DEB estimation, see [`examples/Bos_taurus_Angus`](examples/Bos_taurus_Angus/). 

## Quick Start

A multitier estimation needs four things for each tier: its data, where its entities sit in the hierarchy, the parameters it estimates, and templates for the four DEBtool species files. The main classes are available from the top-level package, and data source types from `DEBtoolPyIF.data_sources`.

```python
from pathlib import Path

from DEBtoolPyIF import (
    CopyFileTemplate,
    DataCollection,
    EstimationTemplates,
    MultiTierStructure,
    MultitierMyDataSubstitutionTemplate,
    RegistryMultitierParsInitProgrammaticTemplate,
    RestartingNelderMead,
    TierHierarchy,
)
from DEBtoolPyIF.data_sources import TimeWeightEntityDataSource

species_name = "My_species"
tier_names = ["population", "individual"]
template_folder = Path("templates")

# 1. Data: one DataCollection per tier
weights = TimeWeightEntityDataSource("weights.csv", id_col="id", weight_col="weight", date_col="date")
data = {
    "population": DataCollection(tier="population", data_sources=[]),
    "individual": DataCollection(tier="individual", data_sources=[weights]),
}

# 2. Hierarchy: the entity each individual belongs to in the tier above
hierarchy = TierHierarchy.from_paths(
    tier_names=tier_names,
    paths=[{"population": "all", "individual": entity_id} for entity_id in sorted(weights.entities)],
)

# 3. Parameters estimated at each tier; lower tiers inherit the rest
tier_pars = {
    "population": ["z", "v", "kap", "p_M"],
    "individual": ["z"],
}

# 4. Templates for the four DEBtool species files of each tier
estimation_templates = {
    tier: EstimationTemplates(
        mydata=MultitierMyDataSubstitutionTemplate(source=template_folder / tier / f"mydata_{species_name}.m"),
        pars_init=RegistryMultitierParsInitProgrammaticTemplate(model="std"),
        predict=CopyFileTemplate(template_folder / tier / f"predict_{species_name}.m"),
        run=RestartingNelderMead(simplex_size=0.25),
    )
    for tier in tier_names
}

multitier = MultiTierStructure(
    species_name=species_name,
    entity_hierarchy=hierarchy,
    data=data,
    tier_pars=tier_pars,
    estimation_templates=estimation_templates,
    output_folder="multitier",
)

# Estimate tier by tier, from the most general to the most specific
estimation_settings = dict(n_runs=3, n_steps=50, n_evals=50000, pars_init_method=2,
                           results_output_mode=0, tol_simplex=1e-4, tol_restart=1e-4)
multitier.tiers["population"].estimate(
    estimation_settings=estimation_settings,
    initial_pars={"z": 13, "v": 0.05, "kap": 0.97, "p_M": 80},
)
multitier.tiers["individual"].estimate(estimation_settings=estimation_settings)
```

Each tier writes its parameters, errors and metadata to `output_folder`. Load them later without rebuilding the workflow:

```python
from DEBtoolPyIF import MultiTierResults

results = MultiTierResults.from_folder(output_folder="multitier", species_name="My_species")
```

About the templates:

- `mydata` and `run` generation are the most mature. A starting `mydata` source with every placeholder is bundled at `DEBtoolPyIF/multitier/resources/generic/mydata_template.m`.
- `pars_init` generation is usable but still evolving. `RegistryMultitierParsInitProgrammaticTemplate` builds the file from the parameters of a typified model (`std` or `stx`), and you can add your own parameter definitions.
- `predict` is specific to each workflow, so it is copied as written. A starting point with the multitier loop structure is bundled at `DEBtoolPyIF/multitier/resources/generic/predict_template.m`.

For a complete, runnable workflow see [`examples/Bos_taurus_Angus`](examples/Bos_taurus_Angus/), and for how templates and sections work see [`docs/parameter_estimation/TEMPLATE_GENERATION.md`](docs/parameter_estimation/TEMPLATE_GENERATION.md).

## Add-my-Pet (experimental)

`DEBtoolPyIF.add_my_pet` downloads species files and parameter sets from the Add-my-Pet collection over HTTP, so it does not need MATLAB. It needs the `amp` extra (see [Installation](#installation)).

```python
from DEBtoolPyIF.add_my_pet import download_species, fetch_species_parameters

download_species("Danio_rerio", "amp")  # mydata, pars_init, predict, run and results files
results = fetch_species_parameters("Danio_rerio", "amp")
results.to_frame()  # value, free, units and label of each parameter
```

This subpackage is experimental, and its functions may change in later releases. The Add-my-Pet server can stop accepting connections after many requests, so please download only the species you need. See [`docs/ADD_MY_PET.md`](docs/ADD_MY_PET.md) for folders, versions and large downloads.

## Installation

You can install DEBtoolPyIF using pip:

```console
pip install DEBtoolPyIF
```

To also use the `DEBtoolPyIF.add_my_pet` subpackage for fetching [Add-my-Pet](https://www.bio.vu.nl/thb/deb/deblab/add_my_pet/) files, install the `amp` extra:

```console
pip install "DEBtoolPyIF[amp]"
```

To use the package you also need to install the MATLAB package DEBtool. 
You can download it from its [GitHub repository](https://github.com/add-my-pet/DEBtool_M).
It is recommended to add the DEBtool folder and all subfolders to the MATLAB path.

Additionally, you will need to install the MATLAB Engine API for Python.
You can find instructions on how to install it in the [official documentation](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).
It is not installed with DEBtoolPyIF, because each MATLAB release needs its own version of it.
DEBtoolPyIF can be imported without it, but running estimations requires it.

### Troubleshooting the installation of the MATLAB Engine API for Python

 Each version of MATLAB has a corresponding version of the `matlabengine` package for Python, so ensure that you are installing the correct version for your MATLAB release. For example, for MATLAB R2025b, you would install version 25.2.2:
```console
pip install matlabengine==25.2.2
```
The version number corresponds to the MATLAB release year, with the major version matching the release year and the minor version indicating the specific release (a for the first release, b for the second release of that year). The last number is the patch version. You can find the correct version to install in the [PyPI repository](https://pypi.org/project/matlabengine/).

If you are having trouble installing the package from PyPI, you can try to install it through the local version by doing the following:

1. Open a terminal in administrator mode.
2. Install from the MATLAB folder
```console
cd "matlabroot\extern\engines\python"
python -m pip install .
```

## Citation

If you use `DEBtoolPyIF`, please cite the software package:

> Oliveira, D. F. (2026). DEBtoolPyIF (Version 0.3.0) [Computer software]. GitHub. https://github.com/diogo-f-oliveira/DEBtool-Python-Interface

```bibtex
@software{oliveira_debtoolpyif_2026,
  author = {Oliveira, Diogo F.},
  title = {DEBtoolPyIF},
  version = {0.3.0},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/diogo-f-oliveira/DEBtool-Python-Interface}
}
```

If you use the multitier methodology implemented in this package, please also cite:

> Oliveira, D. F., Marques, G. M., Carolino, N., Pais, J., Sousa, J. M. C., Domingos, T. (2024). A multi-tier methodology for the estimation of individual-specific parameters of DEB models. Ecological Modelling, 494, 110779. https://doi.org/10.1016/j.ecolmodel.2024.110779

```bibtex
@article{oliveira2024multitier,
  author = {Oliveira, Diogo F. and Marques, Gonçalo M. and Carolino, Nuno and Pais, José and Sousa, João M. C. and Domingos, Tiago},
  title = {A multi-tier methodology for the estimation of individual-specific parameters of DEB models},
  journal = {Ecological Modelling},
  volume = {494},
  pages = {110779},
  year = {2024},
  doi = {10.1016/j.ecolmodel.2024.110779}
}
```
