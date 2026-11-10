# Danio rerio Example (single species, mock data)

This example runs a regular Add-my-Pet style estimation: one species, one set of parameters, no tiers. It shows that the generic template classes work without the multitier machinery.

**All data are mock values.** They were generated from the std model with the parameters in `data.MOCK_TRUE_PARS`, then perturbed by up to ~6% and rounded. Replace `data.load_mock_datasets()` with real data before using the results for anything.

## Running

From the repository root, in the development conda environment:

```powershell
conda run -n debtoolpyif_dev python -m examples.Danio_rerio.estimation --settings fast
```

`--settings end-to-end` runs longer, and `--show-output` shows the MATLAB output. The four species files and `results_Danio_rerio.mat` are written to `examples/Danio_rerio/estimation/`. MATLAB needs DEBtool on its path, as for the Angus example.

## Files

- `data.py`: the mock datasets, plus a prototype of species-level data classes (`ZeroVariateData`, `UnivariateData`) and the `SpeciesDataSection` that renders them into `mydata.m`. The package has no species-level data sources yet (see "Data-source classes for zero-variate species data" in `docs/ROADMAP.md`), so this prototype stays in the example for now.
- `templates.py`: builds `EstimationTemplates` from the generic classes:
  - `mydata`: `MyDataProgrammaticTemplate`, assembled from generic sections and `SpeciesDataSection`,
  - `pars_init`: `RegistryParsInitProgrammaticTemplate` with the std registry plus `del_M`,
  - `predict`: `CopyFileTemplate` of the hand-written `predict_Danio_rerio.m`,
  - `run`: the `NelderMead` algorithm template.
- `estimation.py`: sets initial values, free parameters and run settings on a `SpeciesGenerationContext`, writes the files with `write_estimation_files`, and runs DEBtool with `EstimationRunner`.
- `predict_Danio_rerio.m`: std-model predictions for the datasets in `data.py`, adapted from DEBtool's `predict_my_pet`.

## Datasets

Zero-variate: `ab`, `tp`, `am`, `Lb`, `Lp`, `Li`, `Wwb`, `Wwi`, `Ri`. Univariate: `tL` (time since birth vs total length) and `LW` (total length vs wet weight). Temperatures are 28.5 °C.
