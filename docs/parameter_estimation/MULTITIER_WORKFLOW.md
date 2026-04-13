# Multitier Workflow For Package Users

This guide describes the recommended way to build and run multitier estimation workflows with `DEBtoolPyIF`.

The current preferred workflow constructs `estimation_templates` explicitly in Python and passes them into `MultiTierStructure`.

## What The Multitier Method Does

The multitier workflow estimates DEB parameters from the most general tier down to the most specific tier.

A typical pattern is:

- a broad tier establishes a stable baseline parameterization
- intermediate tiers re-estimate a smaller subset of parameters that vary across subgroups
- the lowest tier re-estimates an even smaller subset for each entity or group

This helps avoid fitting every individual from scratch with too much flexibility and too little data.

## Why Top-Down Order Matters

Tier order is part of the method, not just a display choice.

Higher-tier estimates are reused at lower tiers as:

- initial values for the current tier parameters
- pseudo-data targets that anchor the next fit
- fixed values for parameters that are not being re-estimated at the current tier

Because of that, tiers should be built and estimated from most general to most specific.

## Minimum Objects To Assemble

An end-to-end workflow normally assembles five things:

1. One `DataCollection` per tier
2. One `TierHierarchy` covering the ordered entities across tiers
3. A base parameter dictionary and a `tier_pars` mapping
4. One `estimation_templates` mapping keyed by tier name
5. One `MultiTierStructure` that ties the hierarchy, data, parameters, templates, and outputs together

Once the structure exists, estimation usually runs tier by tier through `multitier.tiers[...]`.

## Recommended Python Project Layout

For user projects, this layout remains the best default:

- `data_sources.py`
  - define any custom entity or group data source classes
  - keep dataset-specific transformation logic close to the class that generates the MATLAB code
- `data.py`
  - load raw files
  - instantiate built-in or custom data source classes
  - return `dict[str, DataCollection]` keyed by tier name
- `templates.py`
  - construct the `estimation_templates` mapping
  - define source templates and Python-side section overrides in one place
- `tier_structure.py`
  - define tier names
  - build the `TierHierarchy`
  - define initial DEB parameters
  - define `tier_pars`
  - instantiate `MultiTierStructure`
- `estimation.py`
  - define estimation settings
  - run tiers in order
  - optionally load saved results back into the tier objects

The Angus example now follows this pattern and should be treated as the canonical reference.

## Recommended Template Pattern

The preferred template workflow is:

1. Use source-backed template classes where MATLAB source remains workflow-specific and benefits from direct review.
2. Use programmatic `pars_init` generation when parameter definitions are available in Python.
3. Use programmatic algorithm templates for `run` when a built-in optimizer captures the desired estimation behavior.
4. Wrap the four file templates for each tier in one `EstimationTemplates` bundle.
5. Pass the tier-name mapping into `MultiTierStructure(..., estimation_templates=...)`.

In practice, this means:

- `mydata` is usually built with `MultitierMyDataSubstitutionTemplate`
- `pars_init` is usually built with `RegistryMultitierParsInitProgrammaticTemplate`
- `predict` is usually wrapped with `CopyFileTemplate`
- `run` should use an algorithm template such as `NelderMead()` when the built-in optimizer behavior fits
- `RunSubstitutionTemplate` remains supported when a project needs to maintain a source-backed MATLAB run script

Algorithm templates own their option set and read render-time values from `estimation_settings`. Source-backed run templates still combine readable MATLAB source with Python-side section rendering, but their placeholders must match registered run section keys such as `$setup`, `$set_options`, and `$estimation_call`.

## Minimal Skeleton

```python
from pathlib import Path

from DEBtoolPyIF import DataCollection, MultiTierStructure, TierHierarchy
from DEBtoolPyIF.estimation_files import EstimationTemplates, CopyFileTemplate
from DEBtoolPyIF.estimation_files.algorithms import NelderMead
from DEBtoolPyIF.multitier import (
    MultitierMyDataSubstitutionTemplate,
    RegistryMultitierParsInitProgrammaticTemplate,
)


def load_data(data_folder: Path) -> dict[str, DataCollection]:
    return {
        "group": DataCollection(tier="group", data_sources=[...]),
        "individual": DataCollection(tier="individual", data_sources=[...]),
    }


def build_estimation_templates(species_name: str, template_root: Path) -> dict[str, EstimationTemplates]:
    return {
        "group": EstimationTemplates(
            mydata=MultitierMyDataSubstitutionTemplate(
                source=template_root / "group" / f"mydata_{species_name}.m",
            ),
            pars_init=RegistryMultitierParsInitProgrammaticTemplate(),
            predict=CopyFileTemplate(
                template_root / "group" / f"predict_{species_name}.m"
            ),
            run=NelderMead(),
        ),
        "individual": EstimationTemplates(
            mydata=MultitierMyDataSubstitutionTemplate(
                source=template_root / "individual" / f"mydata_{species_name}.m",
            ),
            pars_init=RegistryMultitierParsInitProgrammaticTemplate(),
            predict=CopyFileTemplate(
                template_root / "individual" / f"predict_{species_name}.m"
            ),
            run=NelderMead(),
        ),
    }


def create_tier_structure(data, estimation_templates, matlab_session="auto"):
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
        estimation_templates=estimation_templates,
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

## Where Python Customization Belongs

Use `templates.py` for template construction concerns such as:

- choosing template classes
- swapping section objects
- choosing an algorithm template, customizing its options, or composing `RunSection` objects directly
- adding extra `mydata` sections such as temperature or data partition helpers

Use `data_sources.py` and `data.py` for dataset concerns such as:

- parsing raw files
- building entity-level and group-level data sources
- keeping MATLAB variable contracts aligned with the observations

This separation makes it easier to inspect whether a change affects:

- the data being passed into the estimation, or
- the MATLAB files generated from that data

## Recommended Agent Behavior

When helping a user, prefer this order:

1. Identify the tiers and confirm they are ordered from most general to most specific.
2. Decide whether built-in data source classes are enough or whether the user needs custom classes.
3. Build one `DataCollection` per tier.
4. Build the `TierHierarchy` from explicit paths or parent mappings.
5. Choose a conservative `tier_pars` subset for each lower tier.
6. Build `estimation_templates` in Python using the current template classes.
7. Pass those templates into `MultiTierStructure`.
8. Run estimation from top to bottom.
9. Inspect generated outputs and saved tier results before changing the model structure.

## Common Mistakes To Avoid

- Do not estimate tiers out of order.
- Do not make lower-tier `tier_pars` larger just because parameters exist in the base dictionary.
- Do not hide substantial custom data-source logic inside `data.py` when a dedicated `data_sources.py` or `templates.py` would make the workflow clearer.
- Do not bypass `TierHierarchy` by rebuilding hierarchy logic in ad hoc tables.
- Do not treat `predict` as fully abstracted; it is still the most workflow-specific species file.
- Do not assume all file families are equally mature.
  - `mydata` is the most mature
  - `pars_init` and `run` are usable but still evolving
  - `predict` remains largely source-specific

For the deeper implementation details behind these rules, see [MULTITIER.md](MULTITIER.md). For the generation architecture itself, see [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md).
