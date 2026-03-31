# DEBtool File Contracts For Multitier Templates

This document is the main reference for agents that need to generate or edit DEBtool estimation templates for `DEBtoolPyIF`.

It focuses on the concrete MATLAB file contracts:

- the function flow across `run`, `mydata`, `pars_init`, and `predict`,
- the structs each file defines,
- the structs and fields each file consumes,
- which conventions are standard DEBtool and which are multitier-specific.

For the Python-side generation path, see [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md). For the higher-level multitier method, see [MULTITIER.md](MULTITIER.md).

## End-To-End Code Flow

In the current package workflow, the MATLAB side is organized like this:

1. `run_<species>.m` sets DEBtool options and launches estimation with `estim_pars`.
2. During estimation, DEBtool uses `mydata_<species>.m`, `pars_init_<species>.m`, and `predict_<species>.m` as the species-specific contract.
3. After optimization, `run_<species>.m` reloads the result `.mat` file.
4. `run_<species>.m` explicitly calls `mydata_<species>` again to rebuild `data`, `auxData`, `metaData`, `txtData`, and `weights`.
5. `run_<species>.m` removes `par.free` and calls `predict_<species>(q, data, auxData)` to compute `prdData`.
6. `run_<species>.m` saves the final result file with the parameter structs plus the data and prediction structs.

In practice:

- `run` orchestrates,
- `mydata` prepares observations and auxiliary structures,
- `pars_init` prepares the parameter struct for DEBtool,
- `predict` turns parameters plus data context into predictions.

## Standard Outputs And Where They Come From

These are the main MATLAB outputs in the current workflow:

- `mydata_<species>.m`
  - returns `data`, `auxData`, `metaData`, `txtData`, `weights`
- `pars_init_<species>.m`
  - returns `par`, `metaPar`, `txtPar`
- `predict_<species>.m`
  - returns `prdData`, `info`
- `run_<species>.m`
  - saves a results `.mat` file that contains, at minimum, `metaData`, `metaPar`, `par`, `txtPar`, `data`, and `prdData`
  - in current example templates it also saves `auxData`, `txtData`, and `weights`

## `mydata_<species>.m`

Typical function signature:

```matlab
function [data, auxData, metaData, txtData, weights] = mydata_<species>
```

### Code Flow

In the current templates, `mydata` usually does the following:

1. Defines taxonomic and descriptive `metaData`.
2. Defines observed datasets under `data.<varname>`.
3. Defines companion `units.<varname>`, `label.<varname>`, and often `bibkey.<varname>`, `comment.<varname>`, and `title.<varname>`.
4. Defines multitier helper variables such as entity lists and subtree mappings.
5. Calls `setweights(data, [])` to initialize `weights`.
6. Builds `temp` and records data fields into `metaData.data_0` and `metaData.data_1`.
7. Adjusts weights for entity, group, dummy, and pseudo-data variables.
8. Packs `auxData` and `txtData`.

### Structs Defined Here

`data`

- Holds the actual DEB observations.
- Field names are usually dataset-type plus entity or group identifier, such as `tW_PT424401157` or `tJX_grp_Pen_2`.
- Lower-tier templates usually also add pseudo-data under `data.psd.<varname>`.

`metaData`

- Holds species metadata and lists of data fields used by DEBtool.
- Current templates populate fields such as:
  - `metaData.phylum`
  - `metaData.class`
  - `metaData.order`
  - `metaData.family`
  - `metaData.species`
  - `metaData.species_en`
  - `metaData.T_typical`
  - `metaData.COMPLETE`
  - `metaData.data_0`
  - `metaData.data_1`
  - `metaData.data_fields`
- The multitier workflow also mirrors some helper variables into `metaData` so `pars_init` can access them:
  - `metaData.entity_data_types`
  - `metaData.group_data_types`
  - `metaData.entity_list`
  - `metaData.tier_pars`
  - `metaData.tier_par_init_values`

`auxData`

- Holds non-estimated context consumed by `predict`.
- Current multitier templates pack:
  - `auxData.temp`
  - `auxData.tiers`
  - `auxData.init`

`txtData`

- Holds text metadata for DEBtool reporting.
- Current templates typically pack:
  - `txtData.units`
  - `txtData.label`
  - `txtData.bibkey`
  - `txtData.comment`
  - sometimes `txtData.title`

`weights`

- Holds DEBtool weights for each observed variable.
- Dummy helper variables should normally have weight zero so they do not affect estimation.

### Multitier-Specific Structures Created In `mydata`

`tiers`

- This struct is the main multitier helper payload and is later exposed as `auxData.tiers`.
- Current templates use fields such as:
  - `tiers.entity_list`
  - `tiers.tier_entities`
  - `tiers.tier_groups`
  - `tiers.tier_subtree`
  - `tiers.groups_of_entity`
  - `tiers.tier_pars`

`init`

- Stores initial measurement context used by predictions, especially for time-series data.
- Current templates expose it as `auxData.init`.
- Typical examples:
  - `init.tW_<entity_id> = <initial_weight>`
  - `init.tJX_grp_<group_id> = struct(<entity_id> -> <initial_weight>)`

`tier_par_init_values`

- Stored under `metaData.tier_par_init_values`.
- Maps each tier parameter name to the inherited initial value for each current entity.
- Used by `pars_init` to create free tier-specific parameter fields.
- Often also used to define pseudo-data targets in `data.psd`.

### Dummy Helper Variables

Current multitier templates usually create helper variables as DEBtool dummy variables:

- they are written into `data` with a placeholder value such as `10`,
- their metadata is stored in `tiers` and often mirrored into `metaData`,
- their weights are set to zero later.

This allows the workflow to transport hierarchy metadata through the standard DEBtool file structure without letting those variables influence fitting directly.

### What `predict` Expects From `mydata`

Current multitier `predict` templates commonly read:

- `auxData.temp`
- `auxData.tiers.entity_list`
- `auxData.tiers.tier_entities`
- `auxData.tiers.tier_groups`
- `auxData.tiers.tier_subtree`
- `auxData.tiers.groups_of_entity`
- `auxData.tiers.tier_pars`
- `auxData.init`

If a template change removes or renames any of those fields, `predict` usually needs to change with it.

## `pars_init_<species>.m`

Typical function signature:

```matlab
function [par, metaPar, txtPar] = pars_init_<species>(metaData)
```

### Code Flow

In the current templates, `pars_init` usually:

1. Sets `metaPar.model`.
2. Defines base parameter values in `par`.
3. Defines matching `free`, `units`, and `label` fields.
4. Calls `addchem(...)` to add standard chemical parameters.
5. Creates current-tier free parameters such as `par.p_Am_<entity_id>` using `metaData.tier_par_init_values`.
6. Packs `txtPar.units`, `txtPar.label`, and `par.free`.

### Structs Defined Here

`par`

- The main DEB parameter struct passed into DEBtool.
- Base parameters live under names such as `par.p_Am`, `par.kap_X`, `par.v`, and so on.
- Multitier-specific parameters are added as expanded fields, for example:
  - `par.p_Am_CTRL`
  - `par.kap_X_PT424401157`

`par.free`

- Stored as a nested struct on `par`.
- Marks which parameters DEBtool is allowed to estimate.
- In current multitier templates:
  - base inherited parameters are usually fixed with `free.<name> = 0`,
  - current-tier entity-specific parameters are usually free with `free.<name> = 1`.

`metaPar`

- Stores DEB model metadata.
- The current templates at least set `metaPar.model`.

`txtPar`

- Packs descriptive parameter metadata:
  - `txtPar.units`
  - `txtPar.label`

### What `pars_init` Reads

`pars_init` consumes `metaData` from `mydata`, especially:

- `metaData.phylum`
- `metaData.class`
- `metaData.entity_list`
- `metaData.tier_pars`
- `metaData.tier_par_init_values`

This is why the multitier helper values mirrored into `metaData` are part of the contract, not just convenience.

## `predict_<species>.m`

Typical function signature:

```matlab
function [prdData, info] = predict_<species>(par, data, auxData)
```

### Code Flow

Current multitier `predict` templates usually:

1. Initialize `info = 1`.
   This is the success flag, so the template starts by assuming prediction will succeed and only flips `info` to `0` if it encounters an invalid or infeasible case.
2. Initialize group predictions for the estimation tier when that tier has group data.
   The usual source for the relevant group ids is `auxData.tiers.tier_groups.<tier_name>`.
3. Loop through the estimation entities in `auxData.tiers.entity_list`.
4. For the current estimation entity, set the tier-varying parameters by replacing each base parameter in `auxData.tiers.tier_pars` with its entity-specific value from `par.<name>_<entity_id>`.
5. Check whether the resulting parameterization is valid.
   If it is not valid, return `info = 0`.
6. Predict entity-level data for the estimation tier.
7. Predict group-level data for the estimation tier.
   When the current entity contributes to one or more groups, the usual lookup is `auxData.tiers.groups_of_entity.(entity_id)`.
8. Loop through each tier below the estimation tier.
9. For each lower tier, initialize group predictions for that tier when group data exists.
   The usual source is `auxData.tiers.tier_groups.<lower_tier_name>`.
10. For each lower tier, get the relevant descendant entities of the current estimation entity from `auxData.tiers.tier_subtree.(entity_id).<lower_tier_name>`.
11. Loop through those descendant entities and predict their entity-level data.
12. For each descendant entity, predict its group-level contributions using `auxData.tiers.groups_of_entity.(descendant_entity_id)` when needed.
13. Add dummy prediction entries for helper variables so DEBtool remains satisfied with the data layout.

The exact biological equations and numerical steps inside each prediction block are template-specific. The important contract is the tier-wise traversal and the use of the helper structs from `auxData`.

### Structs Read Here

`par`

- Input parameter struct produced by DEBtool.
- In the current run script, `predict` receives `q = rmfield(par, 'free')`, so the `free` flags are removed first.
- Current multitier templates expect both:
  - base parameters such as `par.p_Am`,
  - current-tier expanded parameters such as `par.p_Am_<entity_id>`.

`data`

- Input observed data struct from `mydata`.
- Field names are mirrored by `prdData` when predictions are generated.

`auxData`

- Carries all the non-fitted context needed by the biological prediction logic.
- The multitier-specific contract is mostly under `auxData.tiers` and `auxData.init`.
- `auxData.temp` may also be used for temperature correction or other template-specific auxiliary calculations.

### Structs Defined Here

`prdData`

- Stores predicted values using the same field naming scheme as `data`.
- Group predictions are often accumulated incrementally across lower-tier entities.
- Dummy helper variables are usually assigned placeholder predictions such as `10`.

`info`

- Scalar success flag.
- Current templates return `info = 0` when a parameter set is biologically invalid or a state computation is infeasible.

### Multitier Patterns Inside `predict`

Current templates rely on these patterns:

- `auxData.tiers.entity_list`
  - iterate over the current tier entities being estimated now
- `auxData.tiers.tier_groups.<tier_name>`
  - initialize group predictions for the current tier or for a lower tier before accumulating contributions
- `auxData.tiers.tier_pars`
  - know which base parameters must be overridden with tier-specific values
- `auxData.tiers.tier_subtree.(entity_id).<lower_tier>`
  - find descendant entities in each lower tier that belong to the current estimation entity
- `auxData.tiers.groups_of_entity.(entity_id)`
  - accumulate predictions into group-level observations at the relevant tier
- `auxData.init.<data_varname>`
  - recover initial conditions for time-series predictions

If an agent is authoring a new hierarchy-aware template, this is usually the most important file to reason about.

## `run_<species>.m`

Typical role:

- script, not function
- orchestrates the DEBtool estimation run for one species and one generated tier folder

### Code Flow

Current run templates usually:

1. Define `pets = {'<species>'}` and call `check_my_pet(pets)`.
2. Reset DEBtool options with `estim_options('default')`.
3. Inject settings such as:
  - maximum steps,
  - simplex tolerance,
  - parameter-initialization method,
  - output mode.
4. Call `estim_pars` one or more times.
5. Optionally rerun until the objective stops improving or convergence is reported.
6. Switch DEBtool into a no-optimization reporting mode for final output generation.
7. Load the saved `results_<species>.mat`.
8. Call `mydata_<species>` and `predict_<species>` explicitly to compute `prdData`.
9. Save the final result `.mat` with the updated structs.

### What `run` Injects

`TierCodeGenerator.generate_run_file()` substitutes estimation settings into the run template from the Python `estimation_settings` dict passed into `TierEstimator.estimate(...)`.

The main current placeholders are:

- `n_steps`
- `tol_simplex`
- `pars_init_method`
- `n_runs`
- `results_output_mode`

## Standard DEBtool Vs Multitier-Specific Conventions

Mostly standard DEBtool pieces:

- the four species files
- `data`, `auxData`, `metaData`, `txtData`, `weights`
- `par`, `metaPar`, `txtPar`
- `prdData`, `info`
- the `estim_pars` run loop in `run`

Multitier-specific additions in this package:

- `auxData.tiers`
- `auxData.init`
- multitier helper variables mirrored into `metaData`
- expanded tier-specific parameter names such as `par.<base>_<entity_id>`
- pseudo-data targets for inherited tier parameters at lower tiers
- dummy variables used to carry hierarchy metadata through the DEBtool file contract

## What Agents Must Preserve

- Keep the four standard species file names.
- Keep function signatures aligned with DEBtool expectations.
- Keep the `mydata -> pars_init -> predict` contract consistent across the four files.
- Keep `predict` aligned with the exact field names and nesting emitted by `mydata`.
- Keep `pars_init` aligned with the helper values mirrored into `metaData`.
- Keep field names valid as MATLAB struct fields; entity identifiers must remain uniquely representable in MATLAB.
- Preserve MATLAB-compatible numeric tokens such as `NaN`, `Inf`, and `-Inf`.

## Practical Editing Rule

When changing a multitier template:

- inspect `mydata` and `predict` together,
- treat `auxData.tiers`, `auxData.init`, and `metaData.tier_par_init_values` as the main interface surface,
- verify that every predicted field in `prdData` corresponds to an expected field in `data`,
- only then adjust `pars_init` and `run` if the parameterization or estimation settings contract also changed.
