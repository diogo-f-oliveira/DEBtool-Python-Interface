# Multitier Methodology For Agents

This document is the advanced reference for the multitier DEB estimation workflow implemented in `DEBtoolPyIF`.

If you are helping a package user build or modify a workflow, start with:

1. [README.md](README.md)
2. [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md)
3. [DEBTOOL_FILES.md](DEBTOOL_FILES.md)
4. [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md)

Use this file when you need the deeper implementation and methodology details behind those user-facing guides.

This document explains the multitier DEB estimation methodology implemented in `DEBtoolPyIF`, focusing only on the concepts and package behavior that matter for implementation and maintenance. It is based on:

- `docs/references/Oliveira_et_al_2024_multitier_DEB.pdf`
- `src/DEBtoolPyIF/multitier/structure.py`
- `src/DEBtoolPyIF/multitier/tier_estimation.py`
- `src/DEBtoolPyIF/multitier/codegen.py`
- `src/DEBtoolPyIF/multitier/results.py`
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

In code, tier order is semantic and always runs from most general to most specific. In the
current implementation, `MultiTierStructure` takes a `TierHierarchy` as `entity_hierarchy`, and
the order comes from `entity_hierarchy.tier_names`.

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

### `TierHierarchy` And `entity_vs_tier`

Conceptually, the hierarchy is a tree of entities across ordered tiers. The most direct way to
think about it is:

- each entity belongs to one tier,
- each non-root entity has exactly one parent in the tier above,
- entities may exist in any tier even if they have no children below,
- a path is a contiguous lineage from the root to any existing entity, not necessarily to the
  deepest tier.

This means a top-tier entity such as `female` may legitimately exist with no descendant diet or
individual entities. That is still a valid hierarchy and must not be treated as malformed.

In the current package code, `MultiTierStructure` stores this hierarchy as `entity_hierarchy`.
For transparency and debugging, it also exports a materialized-path view as `entity_vs_tier.csv`.

`entity_vs_tier` is a DataFrame whose:

- index is a `MultiIndex` with levels `('tier', 'entity')`,
- columns are the ordered tier names,
- row values map each entity to the corresponding universe in every tier above or at its own level,
  leaving tiers below that entity empty.

For the Angus example:

- breed row: `male -> male`,
- diet row: `CTRL -> male / CTRL`,
- individual row: `animal_id -> male / diet / animal_id`.

For a hierarchy with an entity that terminates early, a valid row could also look like:

- sex row: `female -> female / NaN / NaN`.

The exported table is useful for inspection, but the live code now answers these questions through
`TierHierarchy`:

- which entities belong to a tier,
- which lower-tier entities belong to a higher-tier entity,
- which higher-tier universe an entity inherits parameter values from.

This table should therefore be read as a materialized-path view of the hierarchy, not as evidence
that every path must reach the deepest tier.

### `DataCollection`

There is one `DataCollection` per tier. It provides:

- all entity-level and group-level data sources for that tier,
- the set of entities and groups,
- group membership lookup,
- generation of MATLAB `mydata` fragments for the entities or groups currently included in an estimation.

This means the hierarchy and the data are separate concerns:

- `TierHierarchy` is the canonical hierarchy object,
- `entity_vs_tier.csv` is a derived materialized-path export,
- `DataCollection` describes available observations inside each tier.

## How `MultiTierStructure` Encodes The Method

`MultiTierStructure` is the orchestration object. It owns estimation flow and parameter inheritance,
but the actual entity relationships live in `entity_hierarchy`.

In the current package layout, the multitier implementation is split by responsibility:

- `structure.py` contains `MultiTierStructure`,
- `tier_estimation.py` contains `TierEstimator`,
- `codegen.py` contains `TierCodeGenerator`,
- `results.py` contains result metadata serialization and save/load helpers.

Important responsibilities:

- preserve tier order,
- create one `TierEstimator` per tier,
- delegate hierarchy navigation to `entity_hierarchy`,
- compute initialization values and inherited parameter dictionaries,
- keep a shared `EstimationRunner` for MATLAB execution.

Key methods:

- `build_tiers()`
  - validates template folders,
  - creates per-tier output folders,
  - instantiates `TierEstimator`.
- `get_init_par_values()`
  - top tier: uses `pars`,
  - lower tiers: uses `entity_hierarchy` to locate the parent entity in the tier above, unless
    pseudo-data overrides it.
- `get_full_pars_dict()`
  - uses `entity_hierarchy.get_path(...)` to assemble the fixed parameter context visible to the
    current tier's MATLAB templates.

## How A Tier Is Estimated

`TierEstimator` is the operational unit for a single tier.

### What It Stores

Each estimator holds:

- `tier_pars`: parameters re-estimated in this tier,
- `pars_df`: estimated parameter values indexed by tier entity,
- `entity_data_errors` and `group_data_errors`: prediction errors collected after estimation,
- template/output folders,
- optional pseudo-data overrides,
- estimation settings for the MATLAB run,
- estimation timestamps and iteration records used by the result metadata helpers in `results.py`.

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

- walks `entity_hierarchy.get_all_tiers_below(self.tier_estimator.name)`,
- gathers relevant entities and groups per tier,
- uses `entity_hierarchy.map_entities(...)` to map the current estimation entities to the related
  entities in each lower tier,
- records subtree membership in `tier_subtree`,
- emits both the actual data variables and the tier-structure helper variables needed by the MATLAB templates.

## Generated MATLAB Structure

The package uses templates because DEBtool expects MATLAB species files in the standard Add-my-Pet layout:

- `mydata_<species>.m`
- `pars_init_<species>.m`
- `predict_<species>.m`
- `run_<species>.m`

For each tier estimation, the templates are filled into a fresh output folder.

At the methodology level, the important point is that these files carry:

- the current tier's observations and inherited context,
- the current tier's free parameters and inherited fixed parameters,
- the hierarchy metadata needed to predict the current tier and all tiers below it,
- the estimation settings for the DEBtool run.

The authoritative file-by-file contract, including function flow, structs, and helper-field expectations, is documented in [DEBTOOL_FILES.md](DEBTOOL_FILES.md). This document stays focused on why those files exist in the multitier method and how the tier logic depends on them.

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
  - `entity_hierarchy.tier_names` must run from most general to most specific.
  - The exported `entity_vs_tier.csv` should reflect that same order.
- Hierarchy paths are contiguous, but they do not need to reach the deepest tier.
  - An entity may exist at any tier without having descendants below it.
- Non-root entities have exactly one parent in the tier above.
  - If the same entity needs to belong to two different parents, it is not a valid tree node and
    should be represented as two distinct entities or with a different model.
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

- malformed `TierHierarchy`,
  - causes wrong inheritance, wrong subtree selection, or empty tier runs;
- stale assumptions that `entity_vs_tier` is the source of truth,
  - causes refactors to reintroduce duplicated hierarchy logic into `MultiTierStructure`;
- assuming every path must reach the deepest tier,
  - incorrectly drops valid entities that legitimately have no descendants;
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
- Structure and orchestration: `src/DEBtoolPyIF/multitier/structure.py`
- Per-tier estimation flow: `src/DEBtoolPyIF/multitier/tier_estimation.py`
- MATLAB file generation: `src/DEBtoolPyIF/multitier/codegen.py`
- Result persistence: `src/DEBtoolPyIF/multitier/results.py`
- Data container behavior: `src/DEBtoolPyIF/data_sources/collection.py`
- Example hierarchy: `examples/Bos_taurus_Angus/tier_structure.py`
- Example data loading: `examples/Bos_taurus_Angus/data.py`
- Example run loop: `examples/Bos_taurus_Angus/estimation.py`
- Example tier templates: `examples/Bos_taurus_Angus/templates/`
