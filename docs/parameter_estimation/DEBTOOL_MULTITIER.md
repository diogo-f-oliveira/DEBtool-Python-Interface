# Multitier Integration In DEBtool Files

This document explains how `DEBtoolPyIF` integrates the multitier estimation methodology into the standard DEBtool species files.

Read [DEBTOOL_FILES.md](DEBTOOL_FILES.md) first for the general DEBtool file structure. This document assumes that baseline and focuses only on the multitier-specific additions.

## What The Multitier Layer Adds

The multitier workflow keeps the standard DEBtool file layout:

- `mydata_<species>.m`
- `pars_init_<species>.m`
- `predict_<species>.m`
- `run_<species>.m`

What changes is that the package injects hierarchy-aware helper data into those files so one estimation tier can:

- estimate the current tier entities,
- include data from the current tier and all tiers below,
- inherit parameter values from the tier above,
- regularize lower-tier fits with pseudo-data,
- traverse descendant entities and grouped observations during prediction.

## Multitier Additions To `mydata`

In `DEBtoolPyIF`, multitier `mydata` generation is the most mature estimation-template path. Generated `mydata` files carry both observations and multitier helper structures.

### Helper Structures Injected Into `mydata`

`tiers`

- Later exposed as `auxData.tiers`.
- Holds the hierarchy metadata needed by `predict`.
- Current fields include:
  - `tiers.entity_list`
  - `tiers.tier_entities`
  - `tiers.tier_groups`
  - `tiers.tier_subtree`
  - `tiers.groups_of_entity`
  - `tiers.tier_pars`

`init`

- Later exposed as `auxData.init`.
- Holds initial measurement context used by lower-tier prediction logic.
- Typical examples:
  - `init.tW_<entity_id> = <initial_weight>`
  - `init.tJX_grp_<group_id> = struct(<entity_id> -> <initial_weight>)`

`metaData.tier_par_init_values`

- Maps each current-tier parameter to an inherited initial value for each estimation entity.
- Used later by `pars_init` and often also by pseudo-data generation.

### Why Dummy Variables Are Used

Current multitier `mydata` sections often transport hierarchy metadata through DEBtool by writing helper values as dummy variables:

- a placeholder value is written into `data`,
- the real helper payload is stored in `tiers`,
- the corresponding weight is set to zero.

This preserves compatibility with the DEBtool file contract while still making the hierarchy available to `predict`.

## Multitier Additions To `pars_init`

The multitier `pars_init` layer keeps the normal DEBtool parameter structs, but expands the current tier parameters into entity-specific fields.

Typical pattern:

- base parameters remain in `par.<name>`
- current-tier free parameters are created as `par.<name>_<entity_id>`
- inherited values from `metaData.tier_par_init_values` become the starting values for those expanded fields

This is how one tier can re-estimate only a subset of parameters while keeping all others fixed from higher-tier estimates or base initialization.

## Multitier Additions To `predict`

The multitier-specific `predict` logic is where the hierarchy becomes operational.

### High-Level Tier Prediction Algorithm

For one estimation tier, the generic multitier prediction pattern is:

1. Initialize group data of the estimation tier.
2. Loop through the estimation entities.
3. Set the current entity's tier-varying parameters from fields such as `par.<name>_<entity_id>`.
4. Check validity of the resulting entity parameterization.
5. Predict entity data of the estimation tier.
6. Predict group data of the estimation tier.
7. Loop through each tier below.
8. Initialize group data of that lower tier.
9. Loop through the descendant entities of that lower tier.
10. Predict entity data for those descendants.
11. Predict group data for those descendants.

The biological equations remain species- and hierarchy-specific, but this traversal pattern is the multitier contract.

### Which Helper Structs `predict` Uses

Current multitier `predict` sources typically read:

- `auxData.tiers.entity_list`
  - the estimation entities of the current tier
- `auxData.tiers.tier_entities`
  - the current tier and all lower tiers, in descending order
- `auxData.tiers.tier_groups.<tier_name>`
  - the group ids for the current tier or a lower tier
- `auxData.tiers.tier_pars`
  - the parameter names that vary in the current tier
- `auxData.tiers.tier_subtree.(entity_id).<lower_tier_name>`
  - the descendant entities governed by the current estimation entity
- `auxData.tiers.groups_of_entity.(entity_id)`
  - the groups each entity contributes to
- `auxData.init.<data_varname>`
  - initial conditions for time-series predictions

If these helper fields change, `predict` usually has to change with them.

## Multitier Pseudo-Data And Inheritance

The multitier workflow uses pseudo-data for tier-to-tier anchoring.

At lower tiers:

- higher-tier estimates become inherited initial values,
- those same inherited values can also become pseudo-data targets,
- the pseudo-data weight controls how strongly lower-tier fits are pulled toward the higher-tier estimate.

In the current package:

- inherited values come from `get_init_par_values()`
- fixed full parameter contexts come from `get_full_pars_dict()`
- pseudo-data weight is passed into generated `mydata`

This is one of the main reasons the multitier workflow must run from the most general tier to the most specific tier.

## How Generated Templates Support The Method

`DEBtoolPyIF` renders tier `estimation_templates` so each tier output folder contains a concrete DEBtool run with:

- the current tier's data plus all lower-tier data,
- the current tier's estimation entities,
- the correct inherited parameter context,
- the helper structs produced by the multitier `mydata` sections and state builders,
- the estimation settings for the MATLAB run.

The Python-side generation path is documented in [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md). The key point here is that generated `mydata` and tier-specific `predict` sources form one joint contract.

## What Current Templates Must Preserve

When editing multitier estimation templates, preserve these invariants:

- `tier_entities`, `tier_groups`, `tier_subtree`, `groups_of_entity`, and `tier_par_init_values` must remain aligned with the prediction logic.
- Lower-tier `predict` logic must traverse the descendant hierarchy implied by `tier_subtree`.
- Group predictions must accumulate over the entities that contribute to each group.
- Expanded parameter fields such as `par.<base>_<entity_id>` must match the names emitted by `pars_init`.
- Lower-tier pseudo-data must stay aligned with the inherited values used to initialize the current tier.

## Relationship To The Other Docs

- [DEBTOOL_FILES.md](DEBTOOL_FILES.md)
  - use for the general DEBtool species-file structure
- [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md)
  - use for how Python renders tier `estimation_templates`
- [MULTITIER.md](MULTITIER.md)
  - use for the broader methodology, hierarchy semantics, and package architecture
