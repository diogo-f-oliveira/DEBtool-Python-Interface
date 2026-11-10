# Bos taurus Angus Example

This example runs a three-tier Angus cattle estimation workflow for breed, diet, and individual tiers.

## Running Estimation

Run the example module from the repository root in the development conda environment:

```powershell
conda run -n debtoolpyif_dev python -m examples.Bos_taurus_Angus.estimation --settings fast
```

The available estimation settings profiles are:

- `fast`: short settings intended for development checks and integration tests. This is the default when `--settings` is omitted.
- `end-to-end`: longer settings intended to run the estimation workflow until convergence.

For the full estimation profile:

```powershell
conda run -n debtoolpyif_dev python -m examples.Bos_taurus_Angus.estimation --settings end-to-end
```

Both commands load the example data, create the multitier structure, and write results under the example's `multitier` output folder.
