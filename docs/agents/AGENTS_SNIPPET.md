# AGENTS.md Snippet For Package Users

Users can copy or adapt the block below into their own `AGENTS.md` when they want Codex or another agent to work effectively with `DEBtoolPyIF`.

```md
## DEBtoolPyIF multitier workflow

- Prefer the top-level imports:
  `from DEBtoolPyIF import DataCollection, MultiTierStructure, TierEstimator, TierHierarchy`
- Structure multitier user code around:
  `data.py`, `tier_structure.py`, and `estimation.py`
- If custom data source classes are needed, define them in `data_sources.py` and keep `data.py` focused on instantiation and `DataCollection` assembly
- Treat repo examples as design references, not required runtime dependencies. The local user project is the source of truth.
- Keep tiers ordered from most general to most specific.
- Build one `DataCollection` per tier and one shared `TierHierarchy` for the full lineage.
- Keep `tier_pars` conservative at lower tiers. Lower tiers should usually re-estimate fewer parameters than higher tiers.
- Preserve the standard DEBtool file names:
  `mydata_<species>.m`, `pars_init_<species>.m`, `predict_<species>.m`, and `run_<species>.m`
- Preserve multitier helper-variable contracts used by `predict`, especially data generated into `mydata_<species>.m`
- When changing estimation logic, prefer editing the tier template files and regenerating outputs rather than manually editing generated MATLAB files.
- Do not assume `examples/` exists in the working environment.
```

## Notes For Users

- Adjust file names or function names only if your project already uses a different structure.
- If your project uses only built-in data source classes, you may not need a separate `data_sources.py`.
- If your hierarchy has more than two tiers, keep the same pattern and add tiers without changing the top-down estimation order.
- If you want deeper background for agents, link them to [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md) and [MULTITIER.md](MULTITIER.md).
