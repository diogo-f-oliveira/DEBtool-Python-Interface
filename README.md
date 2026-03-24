# DEBtool-Python-Interface

`DEBtoolPyIF` is a Python package that interfaces with the MATLAB package DEBtool for Dynamic Energy Budget (DEB) model parameter estimation.

The package currently focuses on two capabilities:
- Template-driven generation of DEBtool species files (`mydata`, `pars_init`, `predict`, `run`) following DEBtool naming and structure conventions.
- A multitier estimation workflow to estimate DEB parameters across hierarchical levels (for example, individual and higher-level entities).

The project is under active development (`0.x`), with the multitier workflow being the most mature part of the package.

## Quick Start Imports

For the main multitier workflow, the package now exposes a curated top-level API:

```python
from DEBtoolPyIF import DataCollection, MultiTierStructure, TierEstimator, TierHierarchy
```

Concrete observation types remain grouped under `DEBtoolPyIF.data_sources`:

```python
from DEBtoolPyIF.data_sources import (
    DigestibilityEntityDataSource,
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
It is recommended to add the DEBtool folder to the MATLAB path.

You also need to install the MATLAB Engine API for Python.
You can find instructions on how to install it in the [official documentation](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).

### Troubleshooting the installation of the MATLAB Engine API for Python

If you are having trouble installing the MATLAB Engine API for Python, you can try the following:

1. Open a terminal in administrator mode.
2. Install from the MATLAB folder
```console
cd "matlabroot\extern\engines\python"
python -m pip install .
```

## Citation

If you use the multitier methodology implemented in this package, please cite:

> Oliveira, D.F, Marques, G.M., Carolino, N., Pais, J.,Sousa, J.M.C., Domingos, T., 2024. A multi-tier methodology for the estimation of individual-specific parameters of DEB models. Ecological Modelling 494, 110779. 
> https://doi.org/10.1016/j.ecolmodel.2024.110779
