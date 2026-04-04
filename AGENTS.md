# AGENTS.md

## Project Purpose
- `DEBtool-Python-Interface` has two primary goals:
  - Provide Python tooling to interface with MATLAB DEBtool, including template-based generation of required species files:
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
- Avoid introducing breaking API changes without updating:
  - example scripts in `examples/`
  - integration tests in `tests/integration/`
- For changes affecting DEBtool generated files, preserve naming and expected DEBtool/add-my-pet conventions unless explicitly requested.
- When generating MATLAB numeric arrays, preserve missing and infinite values as MATLAB-compatible `NaN`, `Inf`, and `-Inf` tokens; do not coerce or drop them.
- Prefer small, targeted patches and keep public constructor signatures explicit.
- Before proposing or implementing new architecture, broad abstractions, large refactors, or changes that may affect future extensibility, review `docs/development_plan.md` and align the design with the roadmap when reasonable.
- For architecture and large-refactor work, prefer designs that preserve compatibility with the current workflow, keep future roadmap options open, and add only lightweight scaffolding for likely future changes when it improves extensibility without adding premature complexity.
- For architecture and large-refactor work, explicitly report that `docs/development_plan.md` was considered and summarize any roadmap-related accommodations, constraints, or tradeoffs in the final write-up.
- If roadmap alignment is unclear, or if multiple plausible directions would support different future roadmap items, ask the user for clarification rather than silently choosing one.

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
