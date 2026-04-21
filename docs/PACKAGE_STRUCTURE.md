# Package Structure

This document gives a compact map of the `DEBtoolPyIF` source tree under `src/DEBtoolPyIF`.

Use it when you need to orient yourself in the codebase quickly, decide where a change belongs, or understand which modules are public workflow surfaces versus lower-level implementation helpers.

For multitier workflow and template-generation behavior, continue with:

- [`docs/parameter_estimation/README.md`](parameter_estimation/README.md)
- [`docs/parameter_estimation/MULTITIER_WORKFLOW.md`](parameter_estimation/MULTITIER_WORKFLOW.md)
- [`docs/parameter_estimation/TEMPLATE_GENERATION.md`](parameter_estimation/TEMPLATE_GENERATION.md)
- [`docs/parameter_estimation/MULTITIER.md`](parameter_estimation/MULTITIER.md)

## Top-Level Package Map

The package is organized by responsibility:

- `__init__.py`
  - curated public API for the main workflow
  - re-exports the primary user-facing classes from `data_sources`, `estimation`, `estimation_files`, `multitier`, and `parameters`
- `data_sources/`
  - Python-side data ingestion layer
  - defines entity and group data-source classes plus `DataCollection`
  - use this area for observation-input modeling, data-source contracts, and collection behavior
- `estimation/`
  - MATLAB execution bridge
  - contains the estimation runner, DEB parametrization problem wrapper, and MATLAB wrapper utilities
  - use this area for logic that launches or coordinates estimation execution rather than generating MATLAB files
- `estimation_files/`
  - generic estimation-file generation framework
  - contains template objects, render context/state helpers, `mydata` generation, `pars_init` generation, `run` generation, algorithm templates, and the file writer
  - this is the core reusable architecture for producing DEBtool species files from Python
- `multitier/`
  - multitier-specific orchestration and template specializations
  - contains hierarchy definitions, tier execution, multitier structure/results, multitier-aware `mydata` and `pars_init` templates, and bundled generic MATLAB templates
  - use this area for code that depends on tier ordering, inherited parameters, or multitier estimation semantics
- `parameters/`
  - parameter-definition and registry layer
  - contains parameter definitions and registry objects used by registry-driven template generation
- `utils/`
  - small shared helpers used across the package
  - includes MATLAB-value conversion and `mydata` code-generation helpers
  - prefer extending shared helpers here instead of adding ad hoc formatting code in feature modules
- `notebook/`
  - notebook-facing helpers and visualizers
  - currently focused on multitier result visualization support
- `add_my_pet/`
  - bundled compatibility assets for the broader DEB/add-my-pet ecosystem
  - not the preferred place for new multitier workflow architecture

## Important Internal Boundaries

- `data_sources` describes the biological or observational inputs.
- `multitier` organizes those inputs into a hierarchy and tier-by-tier estimation workflow.
- `estimation_files` turns Python-side structures into concrete MATLAB species files.
- `estimation` runs those generated files through MATLAB.
- `parameters` provides reusable parameter metadata for template generation.

In practice, many feature changes touch more than one of these areas, but keeping these responsibilities separate helps avoid mixing workflow orchestration, file generation, and MATLAB execution concerns in the same module.

## Main Public Workflow Entry Points

The curated top-level imports in `src/DEBtoolPyIF/__init__.py` are the main public surface:

```python
from DEBtoolPyIF import DataCollection, MultiTierStructure, TierEstimator, TierHierarchy
```

Typical deeper entry points are:

- `DEBtoolPyIF.data_sources`
  - concrete data-source classes such as `TimeWeightEntityDataSource` and `TimeFeedGroupDataSource`
- `DEBtoolPyIF.estimation_files`
  - generic template classes such as `EstimationTemplates`, `CopyFileTemplate`, `MyDataSection`, `ParsInitSection`, `RunSection`, and algorithm templates
- `DEBtoolPyIF.multitier`
  - multitier template variants and hierarchy helpers
- `DEBtoolPyIF.parameters`
  - parameter definitions and registries

## Where To Make Common Changes

- New observation or grouping data type:
  - start in `data_sources/`
- New reusable `mydata`, `pars_init`, or `run` section/template behavior:
  - start in `estimation_files/`
- New multitier-specific helper section, hierarchy-derived state, or tier behavior:
  - start in `multitier/`
- New parameter metadata or registry-backed parameter set:
  - start in `parameters/`
- Shared MATLAB-value rendering or lightweight cross-cutting helper:
  - start in `utils/`
- MATLAB-session launching or estimation-run execution changes:
  - start in `estimation/`

## Related Repo Areas Outside `src/`

- `examples/`
  - source-of-truth examples for the current public multitier workflow
- `tests/`
  - unit tests plus workflow-level integration tests
- `templates/`
  - repo-level template assets outside the installed package tree
- `docs/parameter_estimation/`
  - deeper workflow and architecture references for estimation features

## Notes For Contributors And Agents

- Prefer the curated top-level API and the documented multitier workflow unless a change intentionally expands lower-level package surfaces.
- Treat `estimation_templates` as the preferred workflow for Python-driven DEBtool file generation.
- Treat `template_folder` and folder-conversion helpers as deprecated compatibility paths, not the primary architecture direction.
- `mydata` and `run` generation are the most mature paths, `pars_init` is evolving, and `predict` remains the most workflow-specific generated file.
