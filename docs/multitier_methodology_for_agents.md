# Multitier Methodology For Agents

This document explains the multitier DEB estimation methodology implemented in `DEBtoolPyIF`, focusing only on the concepts and package behavior that matter for implementation and maintenance. It is based on:

- `docs/references/Oliveira_et_al_2024_multitier_DEB.pdf`
- `src/DEBtoolPyIF/multitier/procedure.py`
- `src/DEBtoolPyIF/data_sources/collection.py`
- `examples/Bos_taurus_Angus/`

## Why The Methodology Exists

The package is solving a practical DEB estimation problem:

- Individual-level data is usually too incomplete to identify a full DEB parameter set reliably.
- Using only higher-level averages, such as species or breed means, hides intraspecific variability.
- Fitting all individuals simultaneously would create a very large optimization problem and makes convergence harder.

The multitier method addresses this by estimating parameters sequentially across a hierarchy of statistical universes, from the most general tier down to the most specific tier. In the paper, this reduces the bias-variance problems that appear when trying to estimate individual parameters directly from mixed individual and group data.

In implementation terms, the methodology exists to let us:

- use broad data to identify a stable baseline parameterization,
- re-estimate only a small subset of parameters at more specific tiers,
- carry information from higher tiers downward as initialization and pseudo-data,
- estimate many lower-tier entities independently instead of solving one huge joint problem.

## Core Concepts

### Tier

A tier is a hierarchical level of statistical universes. Typical examples are:

- species or breed,
- trial, diet, or population,
- individual.

The order matters. The package assumes tiers are listed from most general to most specific.

In code, the tier order is the column order of `entity_vs_tier` passed to `MultiTierStructure`.

### Statistical Universe

A statistical universe is the entity being estimated inside a tier:

- one breed in a breed tier,
- one diet in a diet tier,
- one individual in an individual tier.

Each universe gets its own estimate of the tier parameters for that tier.

### Group Data vs Individual Data

The paper distinguishes data by the statistical universe it represents:

- individual data: observed from one organism,
- group data: observed from a group, population, breed, species, or expert-knowledge aggregate.

The implementation reflects this distinction through `DataCollection`, which stores:

- entity data sources,
- group data sources,
- entity/group membership relations.

During estimation of a tier, the package includes data from that tier and all tiers below it.

### Tier Parameters

Each tier only re-estimates a subset of DEB parameters. Those are the tier parameters.

This is central to the method:

- higher tiers can estimate a broader or more general parameter set,
- lower tiers should only re-estimate parameters that are both identifiable and meaningfully variable at that level,
- all non-tier parameters remain fixed from higher-tier estimates or base initial values.

In code, this is the `tier_pars` dict supplied to `MultiTierStructure`.

## The Method In One Pass

For each tier, from top to bottom:

1. Select one statistical universe, or one independent group of universes, to estimate.
2. Include all relevant data from that tier and all tiers below it.
3. Fix all non-tier parameters to values already known from higher tiers.
4. Use higher-tier estimates as both:
   - initial values for the current tier parameters,
   - pseudo-data targets that regularize the current estimation.
5. Run a DEBtool estimation for that tier universe.
6. Save estimated tier parameter values.
7. Use those estimates when building the next tier down.

The top tier anchors the hierarchy with the initial parameter dictionary passed as `pars`.

## Why The Top-Down Order Matters

The paper's motivation is:

- estimating lower-tier parameters directly from mixed data creates bias from broad group data and high variance from flexible individual fits,
- introducing intermediate tiers produces parameter values that are progressively less biased relative to the final lower-tier entities,
- pseudo-data from the previous tier constrains the next tier enough to keep estimates biologically sensible.

The package mirrors this exactly:

- `get_init_par_values()` initializes a tier from the tier above,
- `get_full_pars_dict()` builds the fixed parameter context for generated MATLAB files,
- `estimate()` is normally called tier by tier in insertion order.

If tiers are estimated out of order, lower tiers lose their intended initialization and pseudo-data anchor.

## Package Data Model

### `entity_vs_tier`

`entity_vs_tier` is the backbone of the hierarchy.

It is a DataFrame whose:

- index is a `MultiIndex` with levels `('tier', 'entity')`,
- columns are the ordered tier names,
- row values map each entity to the corresponding universe in every tier above or at its own level.

For the Angus example:

- breed row: `male -> male`,
- diet row: `CTRL -> male / CTRL`,
- individual row: `animal_id -> male / diet / animal_id`.

The package uses this table to answer:

- which entities belong to a tier,
- which lower-tier entities belong to a higher-tier entity,
- which higher-tier universe an entity inherits parameter values from.

### `DataCollection`

There is one `DataCollection` per tier. It provides:

- all entity-level and group-level data sources for that tier,
- the set of entities and groups,
- group membership lookup,
- generation of MATLAB `mydata` fragments for the entities or groups currently included in an estimation.

This means the hierarchy and the data are separate concerns:

- `entity_vs_tier` describes relationships across tiers,
- `DataCollection` describes available observations inside each tier.

## How `MultiTierStructure` Encodes The Method

`MultiTierStructure` is the orchestration object.

Important responsibilities:

- preserve tier order,
- create one `TierEstimator` per tier,
- expose hierarchy navigation helpers,
- compute initialization values and inherited parameter dictionaries,
- keep a shared `EstimationRunner` for MATLAB execution.

Key methods:

- `build_tiers()`
  - validates template folders,
  - creates per-tier output folders,
  - instantiates `TierEstimator`.
- `entities_in_other_tier_from_entity_list()`
  - maps a list of entities in one tier to related entities in another tier.
- `get_init_par_values()`
  - top tier: uses `pars`,
  - lower tiers: uses the estimate from the tier above unless pseudo-data overrides it.
- `get_full_pars_dict()`
  - assembles the fixed parameter set visible to the current tier's MATLAB templates.

## How A Tier Is Estimated

`TierEstimator` is the operational unit for a single tier.

### What It Stores

Each estimator holds:

- `tier_pars`: parameters re-estimated in this tier,
- `pars_df`: estimated parameter values indexed by tier entity,
- `entity_data_errors` and `group_data_errors`: prediction errors collected after estimation,
- template/output folders,
- optional pseudo-data overrides,
- estimation settings for the MATLAB run.

### Estimation Granularity

The implementation deliberately estimates independent universes separately:

- if the tier has only one entity, estimate once in the tier folder;
- if the tier has groups, estimate once per group using the entities in that group;
- otherwise, estimate one entity at a time.

This is the package realization of the paper's efficiency goal: avoid a single high-dimensional optimization over all lower-tier entities.

### Included Data

When estimating tier `T`, the generated MATLAB inputs include observations from:

- tier `T`,
- every tier below `T`.

The code path is `TierCodeGenerator.generate_mydata_file()`, which:

- walks `get_all_tiers_below(self.tier_estimator.name)`,
- gathers relevant entities and groups per tier,
- records subtree membership in `tier_subtree`,
- emits both the actual data variables and the tier-structure helper variables needed by the MATLAB templates.

## Generated MATLAB Structure

The package uses templates because DEBtool expects MATLAB species files in the standard Add-my-Pet layout:

- `mydata_<species>.m`
- `pars_init_<species>.m`
- `predict_<species>.m`
- `run_<species>.m`

For each tier estimation, the templates are filled into a fresh output folder.

### `mydata`

Generated `mydata` contains:

- entity and group datasets included in the current run,
- `entity_data_types` and `group_data_types`,
- `entity_list`,
- `tier_entities`,
- `tier_groups`,
- `tier_subtree`,
- `groups_of_entity`,
- `tier_pars`,
- `tier_par_init_values`.

These helper variables are not incidental. They are how the MATLAB `predict` template learns:

- which lower-tier entities belong to the current tier universe,
- which groups each entity contributes to,
- which parameter names must be expanded as per-entity tier parameters.

### `pars_init`

Generated `pars_init` starts from the fixed parameter context from higher tiers and inserts per-entity initial values for the current tier parameters.

This is how the package encodes the paper's rule that each tier starts from the tier above.

### `predict`

The package usually copies a tier-specific `predict` template unchanged. Those templates implement the biological logic for the specific hierarchy.

They are expected to:

- read the tier helper variables from `auxData.tiers`,
- replace base parameter values with tier-specific values such as `par.<name>_<entity_id>`,
- predict data for the current tier entities and all lower-tier observations they govern.

### `run`

Generated `run` injects estimation settings such as number of runs, iteration limits, and output mode.

## The Role Of Pseudo-Data In This Package

Pseudo-data serves two different roles in the methodology:

1. standard DEB pseudo-data used by DEBtool itself;
2. tier-to-tier anchoring, where a higher-tier estimate becomes the target value for the same parameter at the next tier.

The paper sets the tier pseudo-data weight to `0.1`, and the package exposes this as the `pseudo_data_weight` argument in `TierEstimator.estimate()`. That weight is passed into generated `mydata`.

Implementation details that matter:

- lower-tier initial values come from `get_init_par_values()`,
- lower-tier pseudo-data targets also come from those inherited values,
- `extra_pseudo_data` can override inherited values for specific tier entities,
- pseudo-data is what keeps lower-tier fits from drifting too far just to match sparse local data.

If a lower tier behaves erratically, the first things to inspect are usually:

- whether `tier_pars` is too large,
- whether the inherited values are sensible,
- whether the chosen data can actually identify the proposed tier parameters,
- whether pseudo-data weight is too weak for the amount of local data.

## How The Angus Example Applies The Method

The example in `examples/Bos_taurus_Angus/` is the clearest reference implementation.

Hierarchy:

- `breed`
- `diet`
- `individual`

Data loading:

- `breed`: no direct `DataCollection` data sources,
- `diet`: digestibility data,
- `individual`: weight and grouped feed-intake data.

Tier parameters:

- `breed`: estimates the full initial parameter set,
- `diet`: re-estimates `p_Am`, `kap_X`, `kap_P`,
- `individual`: re-estimates `p_Am`, `kap_X`.

This example illustrates the intended modeling pattern:

- broadest tier establishes a workable DEB parameterization,
- intermediate tier captures meaningful shared variation across a subgroup,
- final tier captures residual individual variation with a smaller parameter subset.

It also shows that lower-tier `predict` files are hierarchy-aware. For example, the diet-level predictor:

- loops over diet entities,
- substitutes diet-specific parameter values,
- uses `tier_subtree` to find individuals under each diet,
- accumulates group predictions from the individual memberships.

## Rules Agents Should Preserve

When changing multitier code or examples, preserve these invariants:

- Tier order is semantic, not cosmetic.
  - Columns in `entity_vs_tier` must run from most general to most specific.
- Lower tiers depend on higher-tier results.
  - A tier should not assume estimates exist unless the tier above has already been run or loaded.
- `tier_pars` must be a subset of parameters known in higher tiers or base `pars`.
  - `build_tiers()` currently validates this.
- Data for a tier includes that tier and all tiers below it.
  - Do not narrow this accidentally unless the methodology is being changed intentionally.
- Lower-tier estimates should stay localized.
  - The code estimates groups or individuals independently whenever possible.
- MATLAB templates are part of the public workflow contract.
  - Generated files must still conform to DEBtool/Add-my-Pet naming and expectations.
- Hierarchy helper variables in `mydata` are required.
  - `tier_entities`, `tier_groups`, `tier_subtree`, `groups_of_entity`, and `tier_par_init_values` are used by tier-specific prediction logic.

## What Usually Goes Wrong

Common implementation failures are:

- malformed `entity_vs_tier`,
  - causes wrong inheritance, wrong subtree selection, or empty tier runs;
- choosing tier parameters that are not identifiable from the data available at that tier and below,
  - causes unstable or biologically implausible fits;
- forgetting that lower-tier templates depend on helper variables generated in `mydata`,
  - breaks prediction logic without necessarily failing loudly at file-generation time;
- changing grouping semantics in `DataCollection`,
  - can silently alter which entities are estimated together;
- running tiers out of order,
  - yields poor initialization and invalid pseudo-data anchoring.

## Practical Guidance For Future Agents

When reading or modifying multitier code, think in this order:

1. What are the tiers and are they ordered correctly?
2. What statistical universe is being estimated in each tier?
3. What data is available for that universe and all tiers below it?
4. Which parameters are allowed to vary in that tier, and why?
5. What values are inherited from the tier above?
6. What MATLAB helper variables must the templates receive for predictions to work?

If a proposed change does not make these answers clearer or safer, it is probably fighting the methodology instead of supporting it.

## Source Pointers

- Paper methodology: `docs/references/Oliveira_et_al_2024_multitier_DEB.pdf`
- Orchestration: `src/DEBtoolPyIF/multitier/procedure.py`
- Data container behavior: `src/DEBtoolPyIF/data_sources/collection.py`
- Example hierarchy: `examples/Bos_taurus_Angus/tier_structure.py`
- Example data loading: `examples/Bos_taurus_Angus/data.py`
- Example run loop: `examples/Bos_taurus_Angus/estimation.py`
- Example tier templates: `examples/Bos_taurus_Angus/templates/`
