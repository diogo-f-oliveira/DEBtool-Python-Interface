# Multitier Workflow For Package Users

This guide describes the recommended way for agents to help users set up multitier estimation with `DEBtoolPyIF`.

## What The Multitier Method Does

The multitier workflow estimates DEB parameters from the most general tier down to the most specific tier.

A typical pattern is:

- a broad tier establishes a stable baseline parameterization,
- intermediate tiers re-estimate a smaller subset of parameters that vary across subgroups,
- the lowest tier re-estimates an even smaller subset for each entity or group.

This helps avoid fitting every individual from scratch with too much flexibility and too little data.

## Why Top-Down Order Matters

Tier order is part of the method, not just a display choice.

Higher-tier estimates are reused at lower tiers as:

- initial values for the current tier parameters,
- pseudo-data targets that anchor the next fit,
- fixed values for parameters that are not being re-estimated at the current tier.

Because of that, tiers should be built and estimated from most general to most specific.

## Minimum Objects To Assemble

An agent normally needs to assemble four things:

1. One `DataCollection` per tier.
2. One `TierHierarchy` covering the ordered entities across tiers.
3. A base parameter dictionary and a `tier_pars` mapping.
4. One `MultiTierStructure` that points to the tier template folders and output folder.

Once the structure exists, estimation usually runs tier by tier through `multitier.tiers[...]`.

## Recommended Python Project Layout

For user projects, follow this layout even when the repo example is not available:

- `data_sources.py`
  - define any custom entity or group data source classes,
  - keep dataset-specific transformation logic close to the class that generates the MATLAB code,
  - import from `DEBtoolPyIF.data_sources.base` when subclassing the package base classes.
- `data.py`
  - load raw files,
  - instantiate built-in or custom data source classes,
  - return `dict[str, DataCollection]` keyed by tier name.
- `tier_structure.py`
  - define tier names,
  - build the `TierHierarchy`,
  - define initial DEB parameters,
  - define `tier_pars`,
  - instantiate `MultiTierStructure`.
- `estimation.py`
  - define estimation settings,
  - run tiers in order,
  - optionally load saved results back into the tier objects.

This mirrors the package example's structure, but adds one extra recommendation: if the user needs any custom data source behavior, put it in `data_sources.py` rather than embedding the class definitions directly in `data.py`.

That separation is the best default because:

- `data.py` stays short and focused on assembling one workflow from local files,
- custom parsing and MATLAB-code-generation logic becomes reusable across tiers or projects,
- agents can inspect or edit data-source behavior without mixing it up with tier construction,
- it becomes clearer which changes affect only loading versus which changes alter the MATLAB data contract.

If a project only needs one very small one-off wrapper, defining it in `data.py` is still acceptable. But for agent-assisted work, a separate `data_sources.py` is the recommended default.

## Custom Data Source Recommendation

Users are not limited to the built-in data source classes. They can define custom classes when their data layout or generated MATLAB variables do not match the package defaults.

The current package extension points are:

- `EntityDataSourceBase` for entity-level datasets
- `GroupDataSourceBase` for group-level datasets
- the zero-variate variants when the dataset is scalar rather than time-series

Recommended pattern for a custom data source:

1. Set a stable `TYPE` that becomes part of the MATLAB variable name.
2. Set `LABELS`, and `AUX_DATA_LABELS` when auxiliary data is generated.
3. Normalize IDs so they remain valid MATLAB field names.
4. Implement `generate_mydata_code(...)` so it emits the expected `data.<TYPE>_<id>` variables.
5. When predictions need initial conditions or other side information, emit matching auxiliary structures such as `init.<varname>`.
6. For group data sources, make sure entity-to-group membership is represented correctly so `DataCollection` can build `entity_vs_group_df`.

As a rule:

- put class definitions in `data_sources.py`,
- put file paths, constructor calls, and `DataCollection(...)` assembly in `data.py`.

## Minimal Skeleton

```python
from DEBtoolPyIF import DataCollection, MultiTierStructure, TierHierarchy


def load_data(data_folder):
    return {
        "group": DataCollection(tier="group", data_sources=[...]),
        "individual": DataCollection(tier="individual", data_sources=[...]),
    }


def create_tier_structure(data, matlab_session="auto"):
    hierarchy = TierHierarchy.from_paths(
        tier_names=["group", "individual"],
        paths=[
            {"group": "A", "individual": "A_01"},
            {"group": "A", "individual": "A_02"},
            {"group": "B", "individual": "B_01"},
        ],
    )

    initial_pars = {
        "p_Am": 5000,
        "kap_X": 0.2,
        "kap_P": 0.1,
    }

    tier_pars = {
        "group": ["p_Am", "kap_X", "kap_P"],
        "individual": ["p_Am", "kap_X"],
    }

    return MultiTierStructure(
        species_name="My_species",
        entity_hierarchy=hierarchy,
        data=data,
        pars=initial_pars,
        tier_pars=tier_pars,
        template_folder="path/to/templates",
        output_folder="path/to/output",
        matlab_session=matlab_session,
    )


def run_multitier_estimation(multitier, estimation_settings):
    for tier_name in multitier.tier_names:
        multitier.tiers[tier_name].estimate(
            save_results=True,
            print_results=False,
            hide_output=True,
            estimation_settings=estimation_settings[tier_name],
        )
```

## Recommended Agent Behavior

When helping a user, prefer this order:

1. Identify the tiers and confirm they are ordered from most general to most specific.
2. Decide whether built-in data source classes are enough or whether the user needs custom classes in `data_sources.py`.
3. Build one `DataCollection` per tier.
4. Build the `TierHierarchy` from explicit paths or parent mappings.
5. Choose a conservative `tier_pars` subset for each lower tier.
6. Point `MultiTierStructure` at per-tier MATLAB template folders.
7. Run estimation from top to bottom.
8. Inspect saved tier results before changing the model structure.

## Common Mistakes To Avoid

- Do not estimate tiers out of order.
- Do not make lower-tier `tier_pars` larger just because parameters exist in the base dictionary.
- Do not assume the user's environment includes the repo examples.
- Do not hide substantial custom data-source logic inside `data.py` when a dedicated `data_sources.py` would make the workflow clearer.
- Do not bypass `TierHierarchy` by rebuilding hierarchy logic in ad hoc tables.
- Do not change DEBtool file names or required helper variables unless the workflow itself is changing.

For the deeper implementation details behind these rules, see [MULTITIER.md](MULTITIER.md).
