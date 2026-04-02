# Tests

This folder contains two complementary test layers.

## Unit tests

`tests/unit/` is for small, fast tests that exercise a single object or behavior with controlled dummy data.

Current scope:
- `test_data_collection_unit.py` covers `DataCollection` behavior with fake entity and group data sources.
- `test_tier_estimation_unit.py` covers tier estimation workflow behavior with fake tier structures and fake estimation runners.
- `test_multitier_results_unit.py` covers multitier result saving/loading, metadata persistence, per-iteration timing, and summary output behavior.
- `multitier_test_helpers.py` provides shared fake multitier structures and runners for the multitier unit tests.
- These tests avoid depending on real example folders or MATLAB.

What the current `DataCollection` unit tests protect:
- adding multiple entity and group sources into one collection
- registration of entity and group data types
- construction of:
  - `entity_vs_data_source_df`
  - `group_vs_data_source_df`
  - `entity_vs_group_df`
- helper methods that navigate entity/group membership
- concatenation of data returned by multiple sources of the same data type
- current missing-key behavior for unknown entities, groups, or data types

Important note:
- These tests currently document the implementation as it exists today, including `KeyError` behavior coming from pandas indexing. If that behavior is intentionally improved later, update these tests to match the new contract rather than keeping accidental behavior forever.

What the current multitier unit tests protect:
- estimation settings handling on `TierEstimator`
- estimation target selection for single-entity, grouped, and mixed grouped-plus-entity tiers
- persisted per-tier result files
- persisted tier timing and per-iteration timing metadata
- load-time restoration of saved metadata
- rejection of unsupported `result_metadata.json` schema versions
- compatibility when `result_metadata.json` is missing
- generation and reconstruction of the higher-level tier result summary

## Integration tests

`tests/integration/` is for workflow-level checks that run against real example packages under `examples/`.

Current discovery contract:
- `tests/integration/conftest.py` discovers examples automatically.
- A folder under `examples/` is treated as an integration-test example when it contains:
  - `data.py`
  - `tier_structure.py`
  - `estimation.py`
  - `data/`

Current example interface expected by the tests:
- `examples/<example>/data.py` defines `load_data(data_folder)`
- `load_data(...)` returns a non-empty `dict[str, DataCollection]`
- `examples/<example>/tier_structure.py` defines `create_tier_structure(data, matlab_session='auto')`
- `create_tier_structure(...)` returns a `MultiTierStructure`
- `examples/<example>/estimation.py` defines `run_multitier_estimation(multitier)`
- examples may also define `load_estimation_results(multitier)` if they want result-loading behavior checked explicitly

Current integration coverage:
- `test_example_data_loading.py`
  - checks that each discovered example has input files in `data/`
  - checks that those inputs are CSV files
  - checks that `load_data()` returns `DataCollection` objects keyed by strings
- `test_multitier_structure.py`
  - checks that `create_tier_structure()` exists
  - checks that it returns a `MultiTierStructure`
  - checks for core attributes used by the workflow: `tier_names` and `tiers`
- `test_estimation_procedure.py`
  - runs the example estimation workflow end to end using the example's own `run_multitier_estimation()` helper
  - redirects outputs to a temporary folder so tests verify fresh artifacts without mutating committed example results
  - checks that each tier writes the current stable result artifacts:
    - `pars.csv`
    - `entity_data_errors.csv`
    - `group_data_errors.csv`
    - `result_metadata.json`
    - `result_summary.json`
  - checks that the detailed CSVs are non-empty and preserve the expected saved index names and data columns
  - checks that metadata and summary outputs contain the expected tier identity, settings, timing, and aggregated summary fields
- `test_result_loading.py`
  - checks example-specific result loading behavior using already-generated estimation outputs
  - currently verifies that the Bos_taurus_Angus example's `load_estimation_results(multitier)` helper restores saved metadata, timing, and per-iteration timing information

## Estimation procedure tests

`test_estimation_procedure.py` and `test_result_loading.py` contain real MATLAB-backed integration tests.

These tests are marked:
- `integration`
- `slow`
- `matlab`

Current assumptions:
- the example exposes `estimation.py` with `run_multitier_estimation(multitier)`
- `create_tier_structure(data, matlab_session='auto')` is the supported way to acquire a MATLAB session for the test
- output verification happens in a temporary folder instead of the example's committed `multitier/` folder
- `tests/integration/conftest.py` exposes a shared `estimated_multitier` fixture that:
  - runs the estimation once per example per pytest session
  - caches the generated outputs
  - allows multiple integration files to reuse the same generated results without relying on test ordering

## Example-specific context

There is currently one example workflow:
- `examples/Bos_taurus_Angus`

From that example, the current integration assumptions are:
- `data.py` builds three `DataCollection` objects keyed by tier name: `breed`, `diet`, and `individual`
- `tier_structure.py` builds a `TierHierarchy` and instantiates `MultiTierStructure`
- `estimation.py` provides the top-level workflow helpers for running estimation and loading saved estimation results

## Guidance for future changes

When adding a new example:
- follow the same `examples/<name>/data.py`, `examples/<name>/tier_structure.py`, `examples/<name>/estimation.py`, and `examples/<name>/data/` layout if you want it picked up automatically by integration tests
- keep `load_data()` and `create_tier_structure()` signatures aligned with the existing examples unless the integration contract is intentionally being changed

When changing `DataCollection`:
- prefer adding or updating unit tests first
- only use integration tests to confirm that example workflows still compose correctly

When expanding estimation coverage:
- keep pure-Python workflow checks separate from MATLAB-dependent execution where possible
- use the existing `slow` and `matlab` markers to protect developer ergonomics
- if multiple integration files need the same expensive estimated outputs, share them through fixtures in `tests/integration/conftest.py` instead of depending on one test file to run before another

## Current Tier Result Contract In Tests

The current tier result contract assumed by the tests is:

- `pars.csv`
  - estimated tier parameters indexed by `entity`
- `entity_data_errors.csv`
  - entity-level errors indexed by `(tier, entity)`
- `group_data_errors.csv`
  - group-level errors indexed by `(tier, group)`
- `result_metadata.json`
  - tier identity
  - tier entities and groups
  - estimated tier parameters
  - estimation settings used
  - overall tier timing
  - per-iteration timing for grouped or entity-level estimation runs
  - per-iteration `relative_output_folder` values relative to the tier output folder
  - no machine-specific absolute paths
- `result_summary.json`
  - compact structured summary for inspection and comparison
  - tier identity and counts
  - ordered `tier_parameters`
  - `elapsed_duration_seconds`
  - `mean_estimated_parameters`
  - `mean_entity_errors_by_tier`
  - `mean_group_errors_by_tier`
