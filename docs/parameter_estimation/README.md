# Guide To DEBtoolPyIF Parameter Estimation Docs

This folder contains shared documentation for humans and agents who are building DEB parameter estimation workflows with `DEBtoolPyIF`.

Start here if the working environment only has the installed package and the user's own project files. Do not assume the repo `examples/` folder is available at runtime.

For a compact map of the package layout outside the estimation-specific docs in this folder, see [`../PACKAGE_STRUCTURE.md`](../PACKAGE_STRUCTURE.md).

## What This Package Exposes

For the main parameter estimation workflow, prefer the curated top-level imports:

```python
from DEBtoolPyIF import DataCollection, MultiTierStructure, TierEstimator, TierHierarchy
```

These are the main concepts agents should organize around:

- `DataCollection` stores the data sources for one tier.
- `TierHierarchy` defines the ordered hierarchy of entities.
- `MultiTierStructure` ties together hierarchy, data, initial parameters, tier parameters, `estimation_templates`, and outputs.
- `TierEstimator` runs one tier and stores its results.

## Recommended Reading Order

Read the docs in this order:

1. [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md) for the recommended user workflow and Python project layout.
2. [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md) for the current template-generation architecture, template classes, section composition, and context/state flow.
3. [DEBTOOL_FILES.md](DEBTOOL_FILES.md) for the general DEBtool estimation-file structure.
4. [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md) for how `DEBtoolPyIF` integrates the multitier methodology into those files.
5. [AGENTS_SNIPPET.md](../agents/AGENTS_SNIPPET.md) for text users can adapt into their own `AGENTS.md`.
6. [MULTITIER.md](MULTITIER.md) for the deeper implementation and methodology reference.

## What Users Should Copy Into Their Own Project

If a user wants agents to work well inside their own project, the recommended local set is:

1. Put the adapted snippet from [AGENTS_SNIPPET.md](../agents/AGENTS_SNIPPET.md) into the project's `AGENTS.md`.
2. Copy [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md) into the project if agents will help build or maintain the Python workflow.
3. Copy [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md) into the project if agents will build or debug `estimation_templates`.
4. Copy [DEBTOOL_FILES.md](DEBTOOL_FILES.md) into the project if agents or users need the general DEBtool file structure reference.
5. Copy [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md) into the project if agents will generate or edit multitier MATLAB templates.
6. Copy [MULTITIER.md](MULTITIER.md) only when agents need the deeper package-internal methodology and architecture reference.

The minimum useful setup is usually:

- a project `AGENTS.md` adapted from [AGENTS_SNIPPET.md](../agents/AGENTS_SNIPPET.md),
- [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md),
- [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md),
- [DEBTOOL_FILES.md](DEBTOOL_FILES.md),
- [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md).

## Working Assumptions For Agents

- Treat the docs in this folder as the primary reference when repo examples are not present locally.
- Follow the example-inspired project layout, but do not hard-code any dependency on `examples/`.
- Keep tiers ordered from most general to most specific.
- Treat `estimation_templates` as the preferred public workflow for template construction.
- Preserve DEBtool file naming and multitier helper-variable contracts unless the user explicitly wants a workflow change.
