# Multitier Methodology And Implementation

This document is the advanced reference for the multitier DEB estimation workflow implemented in `DEBtoolPyIF`.

If you are helping a package user build or modify a workflow, start with:

1. [README.md](README.md)
2. [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md)
3. [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md)
4. [DEBTOOL_FILES.md](DEBTOOL_FILES.md)
5. [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md)

Use this file when you need the deeper methodology and implementation architecture behind those user-facing guides.

This document is based on:

- `docs/references/Oliveira_et_al_2024_multitier_DEB.pdf`
- `src/DEBtoolPyIF/multitier/structure.py`
- `src/DEBtoolPyIF/multitier/tier_estimation.py`
- `src/DEBtoolPyIF/multitier/mydata.py`
- `src/DEBtoolPyIF/multitier/mydata_sections.py`
- `src/DEBtoolPyIF/multitier/pars_init.py`
- `src/DEBtoolPyIF/multitier/estimation_files.py`
- `src/DEBtoolPyIF/estimation_files/*`
- `src/DEBtoolPyIF/estimation_files/writer.py`
- `src/DEBtoolPyIF/multitier/results.py`
- `src/DEBtoolPyIF/data_sources/collection.py`
- `examples/Bos_taurus_Angus/`

## Why The Methodology Exists

The package is solving a practical DEB estimation problem:

- Individual-level data is usually too incomplete to identify a full DEB parameter set reliably.
- Using only higher-level averages, such as species or breed means, hides intraspecific variability.
- Fitting all individuals simultaneously would create a very large optimization problem and makes convergence harder.

The multitier method addresses this by estimating parameters sequentially across a hierarchy of statistical universes, from the most general tier down to the most specific tier.

In implementation terms, the methodology exists to let the package:

- use broad data to identify a stable baseline parameterization
- re-estimate only a small subset of parameters at more specific tiers
- carry information from higher tiers downward as initialization and pseudo-data
- estimate many lower-tier entities independently instead of solving one huge joint problem

## Core Concepts

### Tier

A tier is a hierarchical level of statistical universes.

Typical examples:

- species or breed
- trial, diet, or population
- individual

Tier order is semantic. The package assumes tiers are listed from most general to most specific.

### Statistical Universe

A statistical universe is the entity being estimated inside a tier:

- one breed in a breed tier
- one diet in a diet tier
- one individual in an individual tier

Each universe gets its own estimate of the tier parameters for that tier.

### Group Data vs Individual Data

The implementation reflects the paper's distinction through `DataCollection`, which stores:

- entity data sources
- group data sources
- entity/group membership relations

During estimation of tier `T`, the package includes data from tier `T` and all tiers below it.

### Tier Parameters

Each tier only re-estimates a subset of DEB parameters. Those are the tier parameters.

In code, this is the `tier_pars` mapping supplied to `MultiTierStructure`.

## The Method In One Pass

For each tier, from top to bottom:

1. Select one statistical universe, or one independent group of universes, to estimate.
2. Include all relevant data from that tier and all tiers below it.
3. Fix all non-tier parameters to values already known from higher tiers.
4. Use higher-tier estimates as both:
   - initial values for the current tier parameters
   - pseudo-data targets that regularize the current estimation
5. Render the tier's `estimation_templates` into concrete MATLAB files.
6. Run a DEBtool estimation for that tier universe.
7. Save estimated tier parameter values.
8. Use those estimates when building the next tier down.

The top tier anchors the hierarchy with the initial parameter dictionary passed as `pars`.

## Why The Top-Down Order Matters

The package mirrors the paper's rationale directly:

- `get_init_par_values()` initializes a tier from the tier above
- `get_full_pars_dict()` builds the fixed parameter context for generated MATLAB files
- lower-tier pseudo-data uses those inherited values to anchor the fit

If tiers are estimated out of order, lower tiers lose their intended initialization and pseudo-data anchor.

## Package Data Model

### `TierHierarchy` And `entity_vs_tier`

Conceptually, the hierarchy is a tree of entities across ordered tiers:

- each entity belongs to one tier
- each non-root entity has exactly one parent in the tier above
- entities may exist in any tier even if they have no children below
- a path is a contiguous lineage from the root to any existing entity, not necessarily to the deepest tier

`MultiTierStructure` stores this as `entity_hierarchy`.

For debugging and transparency, it also exports `entity_vs_tier.csv`, a materialized-path view whose rows map each `(tier, entity)` pair onto the ordered tier columns.

### `DataCollection`

There is one `DataCollection` per tier. It provides:

- all entity-level and group-level data sources for that tier
- the set of entities and groups
- group membership lookup
- generation of MATLAB `mydata` fragments for the entities or groups included in the current estimation target

This means:

- `TierHierarchy` owns the hierarchy
- `entity_vs_tier.csv` is a debug export
- `DataCollection` owns the observations available inside each tier

## How `MultiTierStructure` Encodes The Method

`MultiTierStructure` is the orchestration object. It owns estimation flow and parameter inheritance, while the actual entity relationships live in `entity_hierarchy`.

In the current package layout, the multitier implementation is split by responsibility:

- `multitier/structure.py`
  - `MultiTierStructure`
- `multitier/tier_estimation.py`
  - `TierEstimator`
- `multitier/estimation_files.py`
  - multitier generation context helpers
- `multitier/mydata.py`
  - multitier `mydata` template families
- `multitier/mydata_sections.py`
  - multitier-derived state and `mydata` helper sections
- `multitier/pars_init.py`
  - multitier `pars_init` template families
- `estimation_files/*`
  - generic template abstractions and file-family implementations
- `estimation_files/writer.py`
  - final render-and-write step
- `multitier/results.py`
  - result metadata serialization and save/load helpers

Important `MultiTierStructure` responsibilities:

- preserve tier order
- create one `TierEstimator` per tier
- delegate hierarchy navigation to `entity_hierarchy`
- compute initialization values and inherited parameter dictionaries
- hold the tier `estimation_templates` mapping
- keep a shared `EstimationRunner` for MATLAB execution

Key methods:

- `build_tiers()`
  - validates the tier setup
  - creates per-tier output folders
  - instantiates each `TierEstimator`
- `get_init_par_values()`
  - top tier: uses base `pars`
  - lower tiers: inherits from the parent tier unless pseudo-data overrides exist
- `get_full_pars_dict()`
  - assembles the fixed parameter context visible to the current tier

## How A Tier Is Estimated

`TierEstimator` is the operational unit for one tier.

### What It Stores

Each estimator holds:

- `tier_pars`
- `pars_df`
- `entity_data_errors`
- `group_data_errors`
- `estimation_templates` for the tier
- the tier output folder
- optional pseudo-data overrides
- estimation settings
- timestamps and iteration metadata

### Estimation Granularity

The implementation deliberately estimates independent universes separately:

- if the tier has only one entity, estimate once in the tier folder
- if the tier has groups, estimate once per group using the entities in that group
- otherwise, estimate one entity at a time

This keeps the optimization localized instead of forming one very large lower-tier fit.

### Generation Path During Estimation

For each estimation target:

1. `TierEstimator.estimate(...)` resolves the target entity list.
2. It creates the target output folder.
3. It builds `MultitierGenerationContext.from_tier_estimator(...)`.
4. It calls `write_tier_estimation_files(...)` on the tier's normalized template bundle.
5. MATLAB runs on the generated files in that folder.
6. The estimator fetches updated parameter values and errors back into Python.

The important architectural shift is that generation is no longer documented as a monolithic code generator. It is a composition of:

- tier `estimation_templates`
- generation context
- section/state builders
- writer

## Included Data In Generated MATLAB Files

When estimating tier `T`, the generated MATLAB inputs include observations from:

- tier `T`
- every tier below `T`

This now happens through the multitier `mydata` state builder and sections, not through a separate generator class.

At a high level, the multitier `mydata` path:

- walks the tiers below the current tier
- gathers relevant entities and groups per tier
- maps estimation entities to descendant entities through the hierarchy
- records descendant membership in `entity_descendants`
- records ancestor paths in `entity_path`
- emits both observation variables and multitier helper structures

## Generated MATLAB Structure

The package still targets the standard DEBtool species-file contract:

- `mydata_<species>.m`
- `pars_init_<species>.m`
- `predict_<species>.m`
- `run_<species>.m`

What changes in the current architecture is how those files are produced:

- `mydata` is rendered from the most mature multitier template family
- `pars_init` is rendered from multitier-aware parameter-expansion templates
- `predict` is usually copied from a workflow-authored MATLAB source
- `run` is rendered from registry-backed run templates or algorithm templates

For each tier estimation target, these four templates are rendered into one concrete output folder.

## The Role Of Pseudo-Data In This Package

Pseudo-data serves two different roles:

1. standard DEB pseudo-data used by DEBtool itself
2. tier-to-tier anchoring, where a higher-tier estimate becomes the target value for the same parameter at the next tier

The package exposes tier pseudo-data anchoring through `pseudo_data_weight` in `TierEstimator.estimate()`.

Implementation details that matter:

- lower-tier initial values come from `get_init_par_values()`
- lower-tier pseudo-data targets use those inherited values
- `extra_pseudo_data` can override inherited values for specific tier entities
- pseudo-data helps keep lower-tier fits from drifting too far just to match sparse local data

If a lower tier behaves erratically, the first things to inspect are usually:

- whether `tier_pars` is too large
- whether the inherited values are sensible
- whether the chosen data can identify the proposed tier parameters
- whether pseudo-data weight is too weak for the amount of local data

## How The Angus Example Applies The Method

The example in `examples/Bos_taurus_Angus/` is the clearest reference implementation.

Hierarchy:

- `breed`
- `diet`
- `individual`

Tier parameters:

- `breed`
  - estimates the broad starting parameter set
- `diet`
  - re-estimates `p_Am`, `kap_X`, `kap_P`
- `individual`
  - re-estimates `p_Am`, `kap_X`

Generation pattern:

- builds `estimation_templates` explicitly in Python
- uses multitier source-backed template classes for `mydata` and `pars_init`
- uses `CopyFileTemplate` for `predict`
- uses an algorithm template such as `NelderMead` for `run` when built-in optimizer behavior fits

This example is now the canonical reference for the preferred public workflow.

## Current Maturity Of The Four File Families

- `mydata`
  - the most mature generation path
  - the best place to study section composition, derived state, and multitier helper structs
- `pars_init`
  - usable and meaningfully abstracted
  - still less mature than `mydata`
- `run`
  - usable and section-based
  - now has typed option objects and initial algorithm-template support
  - still evolving
- `predict`
  - intentionally still the most workflow-specific file
  - usually best handled as source MATLAB wrapped by `CopyFileTemplate`

## Rules Agents Should Preserve

When changing multitier code or examples, preserve these invariants:

- Tier order is semantic, not cosmetic.
- Non-root entities have exactly one parent in the tier above.
- An entity may exist at any tier without descendants below it.
- Lower tiers depend on higher-tier results.
- `tier_pars` must remain a subset of parameters known in higher tiers or base `pars`.
- Data for a tier includes that tier and all tiers below it unless the methodology is being changed intentionally.
- Multitier helper structures in `mydata` must stay aligned with the hierarchy-aware logic in `predict`.
- Expanded parameter fields such as `par.<name>_<entity_id>` must stay aligned between `pars_init` and `predict`.

## Relationship To The Other Docs

- [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md)
  - use for the recommended user workflow
- [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md)
  - use for template families, sections, and context/state flow
- [DEBTOOL_FILES.md](DEBTOOL_FILES.md)
  - use for the general MATLAB file contract
- [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md)
  - use for the helper-structure contract inside multitier DEBtool files
