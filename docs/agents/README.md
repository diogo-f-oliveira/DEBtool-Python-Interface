# Agent Guide To DEBtoolPyIF

This folder contains agent-facing documentation for package users who are building multitier DEB estimation workflows with `DEBtoolPyIF`.

Start here if the working environment only has the installed package and the user's own project files. Do not assume the repo `examples/` folder is available at runtime.

## What This Package Exposes

For the main multitier workflow, prefer the curated top-level imports:

```python
from DEBtoolPyIF import DataCollection, MultiTierStructure, TierEstimator, TierHierarchy
```

These are the main concepts agents should organize around:

- `DataCollection` stores the data sources for one tier.
- `TierHierarchy` defines the ordered hierarchy of entities.
- `MultiTierStructure` ties together hierarchy, data, initial parameters, tier parameters, templates, and outputs.
- `TierEstimator` runs one tier and stores its results.

## Recommended Reading Order

Read the docs in this order:

1. [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md) for the recommended user workflow and Python project layout.
2. [DEBTOOL_FILES.md](DEBTOOL_FILES.md) for the MATLAB file contracts, code flow, and struct expectations.
3. [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md) for how tier template folders are consumed and generated from Python.
4. [AGENTS_SNIPPET.md](AGENTS_SNIPPET.md) for text users can adapt into their own `AGENTS.md`.
5. [MULTITIER.md](MULTITIER.md) for the deeper implementation and methodology reference.

## What Users Should Copy Into Their Own Project

If a user wants agents to work well inside their own project, the recommended local set is:

1. Put the adapted snippet from [AGENTS_SNIPPET.md](AGENTS_SNIPPET.md) into the project's `AGENTS.md`.
2. Copy [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md) into the project if agents will help build or maintain the Python workflow.
3. Copy [DEBTOOL_FILES.md](DEBTOOL_FILES.md) into the project if agents will generate or edit MATLAB templates.
4. Copy [TEMPLATE_GENERATION.md](TEMPLATE_GENERATION.md) into the project if agents will debug Python-side code generation or generated tier outputs.
5. Copy [MULTITIER.md](MULTITIER.md) only when agents need the deeper package-internal methodology and architecture reference.

The minimum useful setup is usually:

- a project `AGENTS.md` adapted from [AGENTS_SNIPPET.md](AGENTS_SNIPPET.md),
- [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md),
- [DEBTOOL_FILES.md](DEBTOOL_FILES.md).

## Working Assumptions For Agents

- Treat the docs in this folder as the primary reference when repo examples are not present locally.
- Follow the example-inspired project layout, but do not hard-code any dependency on `examples/`.
- Keep tiers ordered from most general to most specific.
- Preserve DEBtool file naming and multitier helper-variable contracts unless the user explicitly wants a workflow change.
