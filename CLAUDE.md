# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The canonical agent instructions live in `AGENTS.md` and are imported below; follow them. This file only adds what is not already there.

@AGENTS.md

## Shell Notes
- The primary shell is Windows PowerShell 5.1 (no `&&`); Git Bash is also available. Commands in `AGENTS.md` are shell-agnostic `conda run ...` invocations.

## Common Commands
- Single test file / single test:
  - `conda run -n debtoolpyif_dev python -m pytest tests/unit/test_data_collection_unit.py -q`
  - `conda run -n debtoolpyif_dev python -m pytest tests/unit/test_data_collection_unit.py::<test_name> -q`
- Unit tests only (fast, no MATLAB): `conda run -n debtoolpyif_dev python -m pytest tests/unit -q`
- Pytest markers defined in `pytest.ini`: `integration`, `slow`, `matlab`.
- Pre-release validation (builds the wheel, installs it into the `debtoolpyif_test` env, runs all examples): `conda run -n debtoolpyif_dev python scripts\release_validate.py` — see `scripts/README.md` for options.
- There is no configured linter/formatter. CI (`.github/workflows/python-publish.yml`) only builds and publishes to PyPI on release; it does not run tests.

## Architecture Big Picture
Responsibility split (details in `docs/PACKAGE_STRUCTURE.md`): `data_sources` → inputs, `multitier` → hierarchy and tier-by-tier orchestration, `estimation_files` → Python-to-MATLAB file generation, `estimation` → MATLAB execution, `parameters` → parameter metadata/registries.

End-to-end flow for one tier:
1. User code (see `examples/Bos_taurus_Angus/`: `data.py`, `templates.py`, `tier_structure.py`, `estimation.py`) builds one `DataCollection` per tier, a shared `TierHierarchy`, and an `estimation_templates` dict of tier name → `EstimationTemplates(mydata=, pars_init=, predict=, run=)`.
2. `MultiTierStructure` (`multitier/structure.py`) creates a `TierEstimator` per tier (`multitier/tier_estimation.py`), ordered general → specific; lower tiers inherit parameters estimated at higher tiers.
3. For each estimation target, the tier estimator builds a generation context (`estimation_files/context.py`, multitier subclass in `multitier/`) and the writer renders the four templates into `mydata_/pars_init_/predict_/run_<species>.m`.
4. `EstimationRunner` (`estimation/runner.py`, via the MATLAB Engine wrapper in `estimation/wrapper.py`) runs DEBtool on those files; results are persisted per tier (`pars.csv`, `entity_data_errors.csv`, `group_data_errors.csv`, `result_metadata.json`, `result_summary.json`) and reloaded through `multitier/results.py`.

Template layer (`estimation_files/templates.py`):
- Three strategies: `CopyFileTemplate` (verbatim, used for `predict`), `ProgrammaticTemplate` (assembled from section objects), `SubstitutionTemplate` (a source `.m` file with placeholders filled by sections).
- `MyDataSection`, `ParsInitSection`, and `RunSection` all derive from `RegisteredTemplateSection`, which auto-registers subclasses per `template_families` in `__init_subclass__` and rejects duplicate keys within a family. This is why section modules must be imported before templates are constructed.
- Multitier variants (`multitier/mydata.py`, `multitier/pars_init.py`, `multitier/mydata_sections.py`) layer tier-aware behavior (inherited parameters, multitier pseudodata/packing, helper variables consumed by `predict`) on top of the generic families.
- Bundled generic MATLAB sources live in `multitier/resources/generic/` (shipped as package data).

Further reading: `docs/parameter_estimation/TEMPLATE_GENERATION.md` (template architecture) and `MULTITIER_WORKFLOW.md` (workflow).
