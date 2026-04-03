# DEBtool Estimation File Structure

This document explains the general structure of DEBtool estimation files.

It is meant for both humans and agents who need to understand how the standard DEBtool species files fit together, what each file defines, and which structs move through the estimation workflow.

For the `DEBtoolPyIF` multitier-specific integration layer, see [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md). For Python-side template generation, see [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md).

## End-To-End Estimation Structure

In the standard DEBtool species workflow, four species files work together:

- `mydata_<species>.m`
- `pars_init_<species>.m`
- `predict_<species>.m`
- `run_<species>.m`

At a high level:

1. `run_<species>.m` configures and launches the estimation.
2. DEBtool uses `mydata_<species>.m`, `pars_init_<species>.m`, and `predict_<species>.m` as the species-specific contract during estimation.
3. After optimization, `run_<species>.m` typically reloads the saved result file.
4. `run_<species>.m` calls `mydata_<species>` to rebuild the data and metadata structs.
5. `run_<species>.m` calls `predict_<species>(par, data, auxData)` or an equivalent parameter struct without free flags to compute predictions.
6. `run_<species>.m` saves the results together with the relevant data and prediction structs.

In practice:

- `run` orchestrates,
- `mydata` prepares observations and metadata,
- `pars_init` prepares the parameter struct,
- `predict` turns parameters plus auxiliary inputs into predictions.

## Standard Outputs

These are the main outputs produced by the four files:

- `mydata_<species>.m`
  - returns `data`, `auxData`, `metaData`, `txtData`, `weights`
- `pars_init_<species>.m`
  - returns `par`, `metaPar`, `txtPar`
- `predict_<species>.m`
  - returns `prdData`, `info`
- `run_<species>.m`
  - typically saves a result `.mat` file containing parameter structs, data structs, and predictions

## `mydata_<species>.m`

Typical function signature:

```matlab
function [data, auxData, metaData, txtData, weights] = mydata_<species>
```

### Code Flow

At a general level, `mydata` usually:

1. Defines descriptive species metadata.
2. Defines observed datasets under `data.<varname>`.
3. Defines companion metadata such as units, labels, bibliography, comments, and titles.
4. Builds any auxiliary inputs needed later by `predict`.
5. Initializes `weights`.
6. Records which data fields are zero-variate versus univariate.
7. Packs the output structs.

### Structs Defined Here

`data`

- Holds the observed datasets used in the estimation.
- Field names are species- and workflow-specific.
- May contain both scalar and vector observations.

`auxData`

- Holds auxiliary inputs needed by `predict`.
- This is the place for non-estimated information that predictions depend on, such as temperatures, initial conditions, or other context.

`metaData`

- Holds species metadata and DEBtool-facing dataset metadata.
- Common fields include:
  - `metaData.phylum`
  - `metaData.class`
  - `metaData.order`
  - `metaData.family`
  - `metaData.species`
  - `metaData.species_en`
  - `metaData.T_typical`
  - `metaData.data_0`
  - `metaData.data_1`
  - `metaData.data_fields`

`txtData`

- Holds text metadata for reporting and interpretation.
- Common fields include:
  - `txtData.units`
  - `txtData.label`
  - `txtData.bibkey`
  - `txtData.comment`
  - sometimes `txtData.title`

`weights`

- Holds the weight of each observed datum in the objective function.

### Generic Editing Invariants

- Every predicted field expected from `predict` should correspond to an observation field in `data`, unless it is an intentional DEBtool dummy variable.
- `metaData.data_0` and `metaData.data_1` should remain aligned with the datasets defined in `data`.
- `auxData` should contain only the auxiliary structures that `predict` actually needs.
- If dummy variables are used, their weights should normally be zero so they do not affect fitting.

## `pars_init_<species>.m`

Typical function signature:

```matlab
function [par, metaPar, txtPar] = pars_init_<species>(metaData)
```

### Code Flow

At a general level, `pars_init` usually:

1. Sets model metadata in `metaPar`.
2. Defines parameter values in `par`.
3. Defines matching `free`, `units`, and `label` fields.
4. Adds any standard chemical parameters or model-specific helper parameters.
5. Packs the output structs.

### Structs Defined Here

`par`

- The main DEB parameter struct.
- Contains the numeric parameter values used by DEBtool.

`par.free`

- Usually stored as a nested struct on `par`.
- Marks which parameters are fixed and which are free to estimate.

`metaPar`

- Holds DEB model metadata.
- Often includes at least `metaPar.model`.

`txtPar`

- Holds text metadata for the parameters.
- Common fields include:
  - `txtPar.units`
  - `txtPar.label`

### What `pars_init` Reads

`pars_init` typically consumes `metaData` from `mydata`, especially taxonomic metadata and any helper metadata needed to define the parameter struct correctly.

### Generic Editing Invariants

- The names in `par`, `par.free`, `txtPar.units`, and `txtPar.label` should remain aligned.
- Any parameter referenced in `predict` should be defined here or introduced by standard DEBtool helper code.
- The parameterization exposed here should match the estimation strategy expected by `run`.

## `predict_<species>.m`

Typical function signature:

```matlab
function [prdData, info] = predict_<species>(par, data, auxData)
```

### Code Flow

At a general level, `predict` usually:

1. Initializes `info = 1`.
   This is the success flag, so prediction starts by assuming success and only flips to `0` if an invalid or infeasible state is encountered.
2. Computes any global auxiliary quantities needed for prediction.
3. Uses `par`, `data`, and `auxData` to compute predicted values for the observed datasets.
4. Stores those predictions in `prdData` using field names aligned with `data`.
5. Returns `info = 0` if the parameter set or state is not biologically or numerically feasible.

The exact biological equations are species- and model-specific, but the contract is that `prdData` mirrors the observation structure expected by DEBtool.

### Structs Read Here

`par`

- Input parameter struct prepared by DEBtool.

`data`

- Input observation struct from `mydata`.

`auxData`

- Input auxiliary context from `mydata`.

### Structs Defined Here

`prdData`

- Holds predicted values corresponding to the observation fields in `data`.

`info`

- Scalar success flag.
- `1` means prediction succeeded.
- `0` means prediction failed for the current parameter set.

### Generic Editing Invariants

- `prdData` field names should stay aligned with the observation fields that DEBtool expects to compare.
- `predict` should only depend on auxiliary inputs that are actually supplied by `mydata`.
- Any failure mode that should invalidate the fit should set `info = 0`.

## `run_<species>.m`

Typical role:

- script, not function
- orchestrates the DEBtool estimation run for one species

### Code Flow

At a general level, `run` usually:

1. Defines the species name through `pets`.
2. Calls `check_my_pet(pets)`.
3. Configures DEBtool estimation options.
4. Calls `estim_pars` one or more times.
5. Switches DEBtool into the final reporting or output mode.
6. Loads the saved result file.
7. Calls `mydata_<species>` and `predict_<species>` explicitly to compute final predictions.
8. Saves the enriched result file.

### What `run` Controls

`run` is where estimation settings, repeated runs, stopping criteria, and final output generation are coordinated.

### Generic Editing Invariants

- The species name in `pets` must match the file naming convention.
- The estimation options set here should be consistent with the parameterization in `pars_init`.
- The final prediction pass should use the same data and parameter conventions expected by `predict`.

## Standard Structs At A Glance

The main DEBtool structs across the workflow are:

- `data`
- `auxData`
- `metaData`
- `txtData`
- `weights`
- `par`
- `metaPar`
- `txtPar`
- `prdData`
- `info`

These are the stable conceptual interfaces. A species-specific or package-specific workflow may add extra fields inside them, but the overall role of each struct should remain clear.

## Practical Rule

When reading or editing a DEBtool species workflow:

1. Start with `run` to understand the orchestration.
2. Read `mydata` to understand the observation and metadata contract.
3. Read `pars_init` to understand the estimated parameterization.
4. Read `predict` to understand how predictions map back to the observed data.

For the `DEBtoolPyIF` multitier integration layer built on top of these files, continue with [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md).
