# AGENTS.md

## Project Purpose
- `DEBtool-Python-Interface` has two primary goals:
  - Provide Python tooling to interface with MATLAB DEBtool, including Python-driven generation of required species files through `estimation_templates`:
    - `mydata_<species>.m`
    - `pars_init_<species>.m`
    - `predict_<species>.m`
    - `run_<species>.m`
  - Implement multitier DEB parameter estimation (individual and higher aggregation levels) based on the published multitier methodology.
- Prefer preserving compatibility with existing example workflows unless explicitly requested otherwise.
- Current status is pre-1.0; prioritize reliability and API clarity to support a near-term major release.

## Environment And Command Defaults
- Always run Python commands in the `debtoolpyif_dev` conda environment.
- Always run tests via conda environment:
  - `conda run -n debtoolpyif_dev python -m pytest ...`
- If a command uses package imports, prefer:
  - `conda run -n debtoolpyif_dev python ...`
- If a command needs `PYTHONPATH`, use:
  - `conda run -n debtoolpyif_dev python -m pytest ...` with `src` layout assumptions handled by project config or explicit env var only when needed.

## Testing Expectations
- For code changes, run relevant tests first, then broader tests if needed.
- Minimum validation for multitier changes:
  - `conda run -n debtoolpyif_dev python -m pytest tests/integration -m integration -q`
- When feasible, run:
  - `conda run -n debtoolpyif_dev python -m pytest -q`
- Keep unit tests fast and isolated from example folders and MATLAB.
- Keep integration tests aligned with the shared example workflow contract under `examples/`.
- When changing `examples/` structure, `load_data`, `create_tier_structure`, or `DataCollection` semantics, review and update both unit and integration tests together.
- See `tests/README.md` for the detailed testing strategy, current example contract, and planned estimation-test scope.
  
## Code Change Guidelines
- Keep path handling robust and cross-platform (`os.path.join` or `pathlib`).
- After introducing breaking API changes update all affected code and tests, including:
  - example scripts in `examples/`
  - integration tests in `tests/integration/`
- Prefer the current public multitier workflow based on `estimation_templates` constructed in Python.
- Treat `template_folder` and folder-conversion helpers as deprecated compatibility paths, not preferred architecture.
- When discussing or updating estimation-file generation, use the current nomenclature:
  - `estimation_templates` for the tier-name mapping passed into `MultiTierStructure`
  - template classes such as `MultitierMyDataSubstitutionTemplate`, `MultitierParsInitSubstitutionTemplate`, `RunSubstitutionTemplate`, and `CopyFileTemplate`
- Use the current example workflow under `examples/` as the source-of-truth for how multitier templates should be built and passed into `MultiTierStructure`.
- Document maturity accurately when relevant:
  - `mydata` and `run` generation are the most mature paths
  - `pars_init` is usable but still evolving
  - `predict` remains the most workflow-specific species file
- `MyDataSection` and `RunSection` intentionally follow the same registry-backed section contract. When adding reusable sections for either file family:
  - define a stable `key`
  - set `template_families` directly on the subclass to opt into automatic discovery
  - set `section_tags` when the section should be selected by tag helpers
  - ensure the custom section module is imported before templates are constructed
- Treat this shared section architecture as the direction for future `pars_init.m` and `predict.m` generation work unless the roadmap or user request says otherwise.
- For `run.m` generation, prefer algorithm templates from `DEBtoolPyIF.estimation_files.algorithms` when a built-in optimizer fits the workflow.
- For custom `run.m` generation, use `RunSection` classes and typed option classes from `run_options.py`.
- The base run template required keys are `setup`, `set_options`, and `estimation_call`.
- Keep optimizer-specific option defaults on algorithm templates, not on the base `RunTemplate` or generic `SetEstimOptionsSection`.
- Use `RunSetting` or `render_key=...` for render-time values from `context.estimation_settings`; typed option classes should validate values after settings are resolved.
- For changes affecting DEBtool generated files, preserve naming and expected DEBtool/add-my-pet conventions unless explicitly requested.
- When generating MATLAB values or code from Python values, use the shared conversion helpers in `src/DEBtoolPyIF/utils/data_conversion.py` or code-generation helpers in `src/DEBtoolPyIF/utils/mydata_code_generation.py`; do not add ad hoc MATLAB value formatters in feature modules.
- When generating MATLAB numeric arrays or scalar values, preserve missing and infinite values as MATLAB-compatible `NaN`, `Inf`, and `-Inf` tokens; do not coerce or drop them.
- Prefer small, targeted patches and keep public constructor signatures explicit.
- Before proposing or implementing new architecture, broad abstractions, large refactors, or changes that may affect future extensibility, review `docs/ROADMAP.md` and align the design with the roadmap when reasonable.
- For architecture and large-refactor work, prefer designs that preserve compatibility with the current workflow, keep future roadmap options open, and add only lightweight scaffolding for likely future changes when it improves extensibility without adding premature complexity.
- For architecture and large-refactor work, explicitly report that `docs/ROADMAP.md` was considered and summarize any roadmap-related accommodations, constraints, or tradeoffs in the final write-up.
- If roadmap alignment is unclear, or if multiple plausible directions would support different future roadmap items, ask the user for clarification rather than silently choosing one.
- When discussing code architecture, optimize for sound design and maintainability rather than agreement. If a user suggestion would add unnecessary complexity, conflict with the roadmap, weaken the API, or otherwise lead to worse code, respectfully push back, explain why, and propose a better alternative.
- Do not be sycophantic in architectural discussions. Treat the shared goal as building the best code and making durable technical decisions, even when that means disagreeing with the user's initial proposal.

## References
- Multitier paper (canonical link): 
  - `docs/references/Oliveira_et_al_2024_Multitier_DEB.pdf`
- Development roadmap:
  - `docs/ROADMAP.md`
- For shared parameter-estimation documentation, prioritize:
  - `docs/parameter_estimation/README.md`
  - `docs/parameter_estimation/MULTITIER_WORKFLOW.md`
  - `docs/parameter_estimation/DEBTOOL_FILES.md`
  - `docs/parameter_estimation/DEBTOOL_MULTITIER.md`
  - `docs/parameter_estimation/TEMPLATE_GENERATION.md`
  - `docs/parameter_estimation/MULTITIER.md`

## Output And Reporting
- After changes, report:
  - files modified
  - behavior change summary
  - exact test commands run and pass/fail outcome
- If tests cannot run, state the concrete blocker and next required action.
