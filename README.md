# DEBtool-Python-Interface

`DEBtoolPyIF` is a Python interface to the MATLAB package DEBtool for Dynamic Energy Budget (DEB) model parameter estimation.

Its most mature current capability is multitier DEB parameter estimation across hierarchical levels, allowing parameters to be estimated from broader tiers down to more specific tiers.

The package also provides template-based generation of DEBtool species files (`mydata`, `pars_init`, `predict`, `run`) that support these workflows while preserving DEBtool naming and structure conventions. Broader AmP/species estimation support is still under development for future versions.

## Learn More

The multitier workflow estimates DEB parameters sequentially across a hierarchy, from broader tiers to more specific ones. In practice, this lets users combine information from higher-level groups with more specific subgroup or individual data, so lower-tier fits start from a stable baseline instead of estimating every parameter from scratch.

This approach is useful when individual-level datasets are too sparse to support full parameter estimation on their own, but higher-level data can help anchor the fit. Typical use cases include estimating parameters across levels such as breed, treatment, population, pen, or individual, while controlling which parameters are re-estimated at each tier.


You can find more details on the multitier workflow and its implementation in [`docs/parameter_estimation/`](docs/parameter_estimation/). The [`README.md`](docs/parameter_estimation/README.md) inside provides a description of what each document covers and how they relate to each other.
For a concrete example of a multitier DEB estimation, see [`examples/Bos_taurus_Angus`](examples/Bos_taurus_Angus/). 

## Quick Start Imports

For the main multitier workflow, the package now exposes a curated top-level API:

```python
from DEBtoolPyIF import DataCollection, MultiTierStructure, TierEstimator, TierHierarchy
```

Concrete observation types remain grouped under `DEBtoolPyIF.data_sources`, e.g.:

```python
from DEBtoolPyIF.data_sources import (
    TimeFeedGroupDataSource,
    TimeWeightEntityDataSource,
)
```

## Installation

You can install DEBtoolPyIF using pip:

```console
pip install DEBtoolPyIF
```

To use the package you also need to install the MATLAB package DEBtool. 
You can download it from its [GitHub repository](https://github.com/add-my-pet/DEBtool_M).
It is recommended to add the DEBtool folder and all subfolders to the MATLAB path.

Additionally, you will need to install the MATLAB Engine API for Python.
You can find instructions on how to install it in the [official documentation](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).

### Troubleshooting the installation of the MATLAB Engine API for Python

 Each version of MATLAB has a corresponding version of the `matlab-engine` package for Python, so ensure that you are installing the correct version for your MATLAB release. For example, for MATLAB R2025b, you would install version 25.2.2:
```console
pip install matlab-engine==25.2.2
```
The version number corresponds to the MATLAB release year, with the major version matching the release year and the minor version indicating the specific release (a for the first release, b for the second release of that year). The last number is the patch version. You can find the correct version to install in the [PyPI repository](pypi.org/project/matlabengine/).

If you are having trouble installing the package from PyPI, you can try to install it through the local version by doing the following:

1. Open a terminal in administrator mode.
2. Install from the MATLAB folder
```console
cd "matlabroot\extern\engines\python"
python -m pip install .
```

## Citation

If you use `DEBtoolPyIF`, please cite the software package:

> Oliveira, D. F. (2026). DEBtoolPyIF (Version 0.2.1) [Computer software]. GitHub. https://github.com/diogo-f-oliveira/DEBtool-Python-Interface

```bibtex
@software{oliveira_debtoolpyif_2026,
  author = {Oliveira, Diogo F.},
  title = {DEBtoolPyIF},
  version = {0.2.1},
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
