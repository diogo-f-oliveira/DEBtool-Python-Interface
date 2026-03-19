# Tests

This folder contains two complementary test layers.

## Unit tests

`tests/unit/` is for small, fast tests that exercise a single object or behavior with controlled dummy data.

Current scope:
- `test_data_collection_unit.py` is the only unit test file at the moment.
- It uses fake subclasses of `EntityDataSourceBase` and `GroupDataSourceBase` instead of real CSV-backed sources.
- The goal is to pin down `DataCollection` behavior without depending on example folders, the filesystem beyond pytest fixtures, or MATLAB.

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

## Integration tests

`tests/integration/` is for workflow-level checks that run against real example packages under `examples/`.

Current discovery contract:
- `tests/integration/conftest.py` discovers examples automatically.
- A folder under `examples/` is treated as an integration-test example when it contains:
  - `data.py`
  - `tier_structure.py`
  - `data/`

Current example interface expected by the tests:
- `examples/<example>/data.py` defines `load_data(data_folder)`
- `load_data(...)` returns a non-empty `dict[str, DataCollection]`
- `examples/<example>/tier_structure.py` defines `create_tier_structure(data, matlab_session='auto')`
- `create_tier_structure(...)` returns a `MultiTierStructure`

Current integration coverage:
- `test_example_data_loading.py`
  - checks that each discovered example has input files in `data/`
  - checks that those inputs are CSV files
  - checks that `load_data()` returns `DataCollection` objects keyed by strings
- `test_multitier_structure.py`
  - checks that `create_tier_structure()` exists
  - checks that it returns a `MultiTierStructure`
  - checks for core attributes used by the workflow: `tier_names` and `tiers`

## Estimation procedure stubs

`test_estimation_procedure.py` is intentionally a placeholder for full end-to-end estimation tests.

These tests are marked:
- `integration`
- `slow`
- `matlab`

The intended future scope is:
- run the estimation workflow end to end for each example
- verify expected output files and naming conventions in the produced multitier folders
- define and test the expected behavior when MATLAB tooling or a MATLAB session is unavailable

## Example-specific context

There is currently one example workflow:
- `examples/Bos_taurus_Angus`

From that example, the current integration assumptions are:
- `data.py` builds three `DataCollection` objects keyed by tier name: `breed`, `diet`, and `individual`
- `tier_structure.py` builds the `entity_vs_tier` table and instantiates `MultiTierStructure`
- `run_estimation.py` shows the intended top-level workflow shape for running or loading estimation results

## Guidance for future changes

When adding a new example:
- follow the same `examples/<name>/data.py`, `examples/<name>/tier_structure.py`, and `examples/<name>/data/` layout if you want it picked up automatically by integration tests
- keep `load_data()` and `create_tier_structure()` signatures aligned with the existing examples unless the integration contract is intentionally being changed

When changing `DataCollection`:
- prefer adding or updating unit tests first
- only use integration tests to confirm that example workflows still compose correctly

When expanding estimation coverage:
- keep pure-Python workflow checks separate from MATLAB-dependent execution where possible
- use the existing `slow` and `matlab` markers to protect developer ergonomics
