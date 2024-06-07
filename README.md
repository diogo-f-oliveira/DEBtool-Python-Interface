# Python Interface for DEBtool

A Python Interface for the MATLAB package DEBtool, a package with tools for Dynamic Energy Budget models.

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
