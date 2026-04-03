# Template Generation In The Multitier Workflow

This guide explains how `DEBtoolPyIF` turns per-tier MATLAB templates into the DEBtool files used for a concrete estimation run.

## Expected Folder Shape

`MultiTierStructure` expects a base template folder that contains one subfolder per tier.

Each tier folder should contain:

- `mydata_<species>.m`
- `pars_init_<species>.m`
- `predict_<species>.m`
- `run_<species>.m`

The package validates that every tier listed in `TierHierarchy` has a matching template folder.

## How The Python Objects Use The Templates

The flow is:

1. `MultiTierStructure.build_tiers()` checks that each tier has a template folder and creates one `TierEstimator` per tier.
2. Each `TierEstimator` owns a `TierCodeGenerator`.
3. During `TierEstimator.estimate(...)`, the code generator writes a fresh set of MATLAB files into the current tier output folder, or into a subfolder for the current group or entity target.
4. The estimation runner then executes DEBtool against those generated files.

## What Gets Substituted

### `mydata`

`TierCodeGenerator.generate_mydata_file(...)` fills the template with:

- entity-level and group-level data code,
- data-type metadata,
- the current entity list,
- tier membership metadata,
- subtree and grouping helper variables,
- tier parameter names,
- inherited initial values for the current tier parameters,
- estimation extras such as pseudo-data weight and optional extra info.

### `pars_init`

`TierCodeGenerator.generate_pars_init_file(...)` fills the template using the parameter dictionary assembled from:

- the base `pars` passed into `MultiTierStructure`,
- any already-estimated higher-tier parameter values that should now be fixed,
- the current tier's inherited initial values.

### `predict`

`TierCodeGenerator.generate_predict_file()` usually copies the template as-is.

This is intentional: prediction logic is often too specific to each hierarchy to be safely reconstructed from Python substitutions alone.

### `run`

`TierCodeGenerator.generate_run_file()` fills the template from the `estimation_settings` dictionary supplied to `TierEstimator.estimate(...)`.

## What Users And Agents Should Customize

Safe and expected customization points:

- the tier hierarchy itself,
- the tier-specific parameter subsets in `tier_pars`,
- the data-loading code that produces `DataCollection` objects,
- tier template contents, especially `predict_<species>.m`,
- estimation settings passed into each tier run.

Workflow contracts agents should preserve:

- one template folder per tier,
- the four standard species file names inside each tier folder,
- tier order matching the hierarchy order,
- helper-variable compatibility between generated `mydata` and tier-specific `predict` code.

## Practical Rule

If the user's request is about changing biology or tier logic, edit the tier templates and Python setup.

If the request is about understanding a failed run, inspect the generated MATLAB files in the tier output folders to see the final concrete inputs that DEBtool received.

For the general DEBtool species-file structure, see [DEBTOOL_FILES.md](DEBTOOL_FILES.md). For the multitier-specific helper structures and prediction integration layer, see [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md).
