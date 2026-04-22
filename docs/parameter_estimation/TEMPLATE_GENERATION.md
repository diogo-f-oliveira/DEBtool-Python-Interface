# Template Generation With `estimation_templates`

This guide explains the current estimation-template architecture in `DEBtoolPyIF`.

Use this document when you need to understand how Python-side template objects become concrete MATLAB species files for one multitier estimation target.

## Canonical Flow

The current generation path is:

1. `MultiTierStructure` receives an `estimation_templates` mapping keyed by tier name.
2. Each tier mapping entry bundles four template objects in one `EstimationTemplates` instance:
   - `mydata`
   - `pars_init`
   - `predict`
   - `run`
3. `TierEstimator.estimate(...)` selects one estimation target for the current tier.
4. The tier estimator builds a `MultitierGenerationContext` for that target.
5. `write_tier_estimation_files(...)` renders the four templates against that context and writes:
   - `mydata_<species>.m`
   - `pars_init_<species>.m`
   - `predict_<species>.m`
   - `run_<species>.m`
6. MATLAB then runs the estimation against those generated files.

At the API level, the important object is not a folder path but the `estimation_templates` mapping that `MultiTierStructure` consumes.

## What One Tier Owns

For one tier, the package treats the species-file set as one template bundle:

class EstimationTemplates:
pass

```python
EstimationTemplates(
    mydata=...,
    pars_init=...,
    predict=...,
    run=...,
)
```

An `estimation_templates` mapping is therefore a tier-name-to-template-bundle mapping.

Typical structure:

```python
estimation_templates = {
    "breed": EstimationTemplates(...),
    "diet": EstimationTemplates(...),
    "individual": EstimationTemplates(...),
}
```

`MultiTierStructure(..., estimation_templates=estimation_templates, ...)` then normalizes that mapping and passes the tier-specific bundle into each `TierEstimator`.

## Template Class Families

The template layer is intentionally split by behavior.

### Core generic template strategies

`CopyFileTemplate`

- Target: any file whose source should be copied verbatim.
- Style: verbatim-copy.
- Customization: edit the source file directly.
- Current use: primarily `predict`, where biology and hierarchy logic are still highly workflow-specific.
- Current maturity: stable as a thin pass-through wrapper.

`ProgrammaticTemplate`

- Target: any estimation file that can be assembled from validated sections.
- Style: fully programmatic section assembly.
- Customization: choose or replace section objects in Python.
- Current use: base behavior for programmatic `mydata`, `pars_init`, and `run` variants.
- Current maturity: stable as an abstraction; maturity depends on the concrete file family using it.

`SubstitutionTemplate`

- Target: any file that starts from a source string or file with named placeholders.
- Style: placeholder substitution driven by matched sections.
- Customization: edit the source template and optionally override section objects in Python.
- Current use: base behavior for source-backed `mydata`, `pars_init`, and `run` variants.
- Current maturity: stable as an abstraction; especially useful when users want readable MATLAB template sources.

### `mydata` template families

`MyDataProgrammaticTemplate`

- Target: generic `mydata`.
- Style: programmatic.
- Customization: provide `MyDataSection` objects directly.
- Current use: generic `mydata` generation outside multitier-specific helpers.
- Current maturity: usable, but the most developed path is the multitier subclass.

`MyDataSubstitutionTemplate`

- Target: generic `mydata`.
- Style: placeholder-substitution.
- Customization: start from a source template with `mydata` keys such as `$function_header` or `$entity_data_block`.
- Current use: source-backed generic `mydata`.
- Current maturity: usable, but less central than the multitier subclass for current package workflows.

`MultitierMyDataProgrammaticTemplate`

- Target: multitier `mydata`.
- Style: programmatic.
- Customization: assemble or replace multitier-aware `MyDataSection` objects directly in Python.
- Current use: programmatic construction of the most mature estimation-template family in the package.
- Current maturity: highest among the four species-file families.

`MultitierMyDataSubstitutionTemplate`

- Target: multitier `mydata`.
- Style: placeholder-substitution.
- Customization: start from a readable MATLAB source template and bind multitier-aware sections to the placeholders it references.
- Current use: the canonical pattern for current workflows and examples.
- Current maturity: highest among the four species-file families.

### `pars_init` template families

`ParsInitProgrammaticTemplate`

- Target: generic `pars_init`.
- Style: programmatic.
- Customization: compose generic `ParsInitSection` objects directly.
- Current use: low-level generic `pars_init` section assembly.
- Current maturity: usable, but still evolving compared with `mydata`.

`RegistryParsInitProgrammaticTemplate`

- Target: generic `pars_init`.
- Style: programmatic.
- Customization: provide a parameter registry, model name, or addchem flag to build the default section set. The model defaults to `"std"`. Built-in registries are available for `"std"` and `"stx"`; `"nat"` requires an explicit custom `ParameterRegistry`.
- Current use: automated parameter-struct construction from parameter definitions.
- Current maturity: usable, but still evolving compared with `mydata`.

`RegistryParsInitSubstitutionTemplate`

- Target: generic `pars_init`.
- Style: placeholder-substitution.
- Customization: provide a parameter registry, model name, or addchem flag while rendering through source placeholders. The model defaults to `"std"` and `"nat"` requires an explicit custom registry.
- Current use: source-backed automated parameter-struct construction from parameter definitions.
- Current maturity: usable, still evolving.

`ParsInitSubstitutionTemplate`

- Target: generic `pars_init`.
- Style: placeholder-substitution.
- Customization: edit a source template with registered section keys such as `$function_header`, `$base_parameters`, and `$packing`; pass custom `ParsInitSection` objects when default section behavior should change.
- Current use: source-backed generic `pars_init`.
- Current maturity: usable, still evolving.

`MultitierParsInitProgrammaticTemplate`

- Target: multitier `pars_init`.
- Style: programmatic.
- Customization: use the multitier loop-expansion section programmatically.
- Current use: automatic expansion of current-tier parameter names into entity-specific free fields.
- Current maturity: usable, still evolving.

`RegistryMultitierParsInitProgrammaticTemplate`

- Target: multitier `pars_init`.
- Style: programmatic.
- Customization: provide a parameter registry, model name, or addchem flag while using programmatic section assembly. The model defaults to `"std"` and `"nat"` requires an explicit custom registry.
- Current use: preferred multitier `pars_init` generation when parameter definitions are available in Python.
- Current maturity: usable, still evolving.

`MultitierParsInitSubstitutionTemplate`

- Target: multitier `pars_init`.
- Style: placeholder-substitution.
- Customization: start from a source template and bind multitier sections such as `tier_parameter_loops`.
- Current use: the main multitier `pars_init` source-backed path.
- Current maturity: usable, still evolving.

`RegistryMultitierParsInitSubstitutionTemplate`

- Target: multitier `pars_init`.
- Style: placeholder-substitution.
- Customization: provide a parameter registry, model name, or addchem flag while rendering multitier source placeholders. The model defaults to `"std"` and `"nat"` requires an explicit custom registry.
- Current use: source-backed multitier parameter generation when species-specific parameter definitions are needed.
- Current maturity: usable, still evolving.

### `run` template families

`RunProgrammaticTemplate`

- Target: `run`.
- Style: programmatic.
- Customization: compose `RunSection` objects such as `setup`, `set_options`, and `estimation_call` in Python.
- Current use: low-level generic `run` script assembly.
- Current maturity: usable, still evolving.

`RunSubstitutionTemplate`

- Target: `run`.
- Style: placeholder-substitution.
- Customization: edit a source script with registered run section placeholders such as `$setup`, `$set_options`, and `$estimation_call`.
- Current use: source-backed `run` customization when a project needs readable MATLAB source templates.
- Current maturity: usable, still evolving.

Algorithm templates in `DEBtoolPyIF.estimation_files.algorithms`, such as `NelderMead`, are the preferred higher-level entry point when the built-in optimizer behavior fits the workflow. These templates subclass `AlgorithmRunTemplate`, which itself builds on `RunProgrammaticTemplate`, and own their optimizer-specific option set and post-estimation sections.

### Current maturity summary

- `mydata` is the most mature generation path and should be used as the main mental model for how the template architecture works.
- `pars_init` and `run` already have meaningful abstractions and are usable, but they are still less complete than `mydata`.
- `predict` is intentionally still mostly source-specific and is best thought of as a workflow-authored MATLAB file wrapped by `CopyFileTemplate`.

## Section Composition

The package uses sections to keep file-family logic composable.

### Section contracts

`ParsInitSection`

- Used by `pars_init`.
- Each section renders one canonical `pars_init` key.
- Section classes can opt into automatic discovery by declaring `template_families` and optional `section_tags`.
- Required base `pars_init` keys are `function_header`, `model_metadata`, `base_parameters`, `addchem`, and `packing`.
- `allowed_section_keys()` is derived from the `ParsInitSection` registry.
- Duplicate registered keys are rejected within the same template family.

`RunSection`

- Used by `run`.
- Each section renders one canonical `run` key.
- Section classes can opt into automatic discovery by declaring `template_families` and optional `section_tags`.
- Required base `run` keys are `setup`, `set_options`, and `estimation_call`.
- `allowed_section_keys()` is derived from the `RunSection` registry.
- Duplicate registered keys are rejected within the same template family.

`MyDataSection`

- Used only for `mydata`.
- Each section renders one canonical `mydata` key and receives both the render context and a precomputed `BaseMyDataState`.
- Section classes can opt into automatic discovery by declaring `template_families` and optional `section_tags`.

`mydata` is special because many of its sections need shared derived state, not just direct access to the top-level context.

### `pars_init` sections

`ParsInitSection` follows the same registry pattern as `RunSection` for the `pars_init` file family:

- define a stable `key`
- set `template_families = ("pars_init",)` directly on the subclass to opt into discovery
- set `section_tags` when the section should be selectable by tag helpers
- import custom section modules before constructing templates

Built-in generic pars-init sections include:

- `ParsInitFunctionHeader`
- `AddModelMedatadaSection`
- `InitializeParametersSection`
- `ParsInitAddChemSection`
- `ParsInitChemicalParametersSection`
- `ParsInitPackingSection`

The multitier family adds `MultitierParsInitLoopsSection` through `template_families = ("multitier_pars_init",)`.

### Parameter definition catalog

Reusable parameter metadata lives in `DEBtoolPyIF.parameters.definitions`.

- Import named DEBtool-style objects when code needs direct reuse, for example `from DEBtoolPyIF.parameters import p_Am`.
- Use `get_parameter_definition(name)` or `require_parameter_definition(name)` for dynamic lookup.
- Use `get_parameter_registry_of_typified_model("std")` or `...("stx")` for built-in typified-model registries.
- Use `ParameterRegistry(...)` directly for custom or `nat` workflows.
- Use `DEBtoolPyIF.parameters` directly only when you specifically need the concrete typified registry classes.
- Add non-default reusable definitions, such as `p_Am`, `t_0`, `E_Hx`, and `del_M`, deliberately when a model or example needs them.
- Define species- or workflow-specific parameters, such as Angus-only female parameters, next to that workflow and add them to the registry there.

Chemical override helpers live in `DEBtoolPyIF.parameters.chemical`.

- `ChemicalParameters` groups the standard chemical definitions for one compound: `mu`, `n_C`, `n_H`, `n_O`, and `n_N`.
- `get_chemical_parameters_of(...)` accepts either a standard compound symbol such as `"N"` or a standard name such as `"n-waste"` and returns one grouped `ChemicalParameters` object.
- `get_chemical_parameter_values_of(...)` returns a ready-to-render `ChemicalParameterValues` object with built-in defaults for standard compounds and selected named variants such as `ammonia`, `urea`, `uric acid`, and `methane`.
- `ChemicalParameterValues.from_common_compound(...)` and `.from_compound(...)` are convenience constructors when the workflow should build render values in one call.
- These chemical definitions are intentionally not added to the default parameter registries because `addchem(...)` remains the baseline source of DEBtool chemical defaults.
- Use them when a workflow needs explicit non-default chemical overrides rendered after `addchem(...)`.

### `run` sections and options

`RunSection` follows the same registry pattern as `MyDataSection` for the `run` file family:

- define a stable `key`
- set `template_families = ("run",)` directly on the subclass to opt into discovery
- set `section_tags` when the section should be selectable by tag helpers
- import custom section modules before constructing templates

Built-in run sections include:

- `RunSetupSection`
  - renders the standard `clear`, `close all`, `global pets`, species list, and `check_my_pet(pets)` setup
- `SetEstimOptionsSection`
  - renders DEBtool estimation option initialization and an ordered set of typed option objects
- `EstimationCallSection`
  - renders the base DEBtool entry point, `estim_pars`
- `RestartLoopSection`
  - renders the restarting Nelder-Mead loop after an initial `estim_pars` call
  - uses `n_runs` and `tol_restart` settings
- `GetResultsSection`
  - reloads parameters from the result file, disables estimation with `method='no'`, sets `results_output`, and calls `estim_pars` to save requested output
- `SavePredictionsSection`
  - reloads the DEBtool result file, rebuilds data, calls `predict`, and saves predictions with the result data

`run_options.py` owns the typed `estim_options(...)` rendering layer.

`RunSetting`

- Represents a render-time lookup from `context.estimation_settings`.
- `render_key="n_steps"` is convenience syntax for `RunSetting("n_steps")`.

`EstimOption`

- Base class for one typed `estim_options(...)` call.
- Resolves any `RunSetting` before validation.
- Supports fixed construction-time values and render-time values.
- Supports optional variable creation for options that should first be assigned to a MATLAB variable.

Typed option bases:

- `NumericEstimOption`
  - renders with `convert_numeric_array_to_matlab(...)`
- `IntegerEstimOption`
  - validates whole-number DEBtool options such as counts and numeric mode flags
  - renders with `convert_numeric_array_to_matlab(...)`
- `StringEstimOption`
  - renders with `convert_string_to_matlab(...)`

Named option classes include:

- `SetMaxStepNumberOption`
- `SetMaxFunEvalsOption`
- `SetSimplexSizeOption`
- `SetFilterOption`
- `SetTolSimplexOption`
- `SetParsInitMethodOption`
- `SetResultsOutputOption`
- `SetMethodOption`

Examples:

```python
from DEBtoolPyIF.estimation_files import (
    RunSetting,
    SetEstimOptionsSection,
    SetMaxStepNumberOption,
    SetMethodOption,
)

fixed = SetMaxStepNumberOption(500)
from_render_key = SetMaxStepNumberOption(render_key="n_steps")
from_setting = SetMaxStepNumberOption(RunSetting("n_steps"))

section = SetEstimOptionsSection(
    options=(
        SetMethodOption("nm"),
        SetMaxStepNumberOption(render_key="n_steps"),
    )
)
```

`SetDefaultEstimOptions` renders the package's MATLAB code for default DEBtool estimation options. `SetEstimOptionsSection(options=None)` and `SetEstimOptionsSection(options=())` render only this default initialization; they do not provide shared algorithm defaults. Optimizer-specific defaults belong on algorithm templates such as `NelderMead`.

`AlgorithmRunTemplate`

- Base class for optimizer-specific `run.m` templates.
- Subclasses define `method`, `option_classes`, and `get_algorithm_settings()`.
- Constructor values are rendered directly into `estim_options(...)`.
- Omitted constructor values become render-time keys resolved from `context.estimation_settings`.
- Accepts `add_path_dirs=...` for fixed MATLAB folders rendered as `addpath(...)` after setup.
- `get_algorithm_settings()` may include non-`estim_options` settings used by algorithm sections.
- `build_algorithm_options()` renders only settings declared in `option_classes`.
- `get_fixed_settings()` returns constructor-provided settings.
- `get_render_time_settings()` returns omitted settings that must be supplied at render time.

`NelderMead`

- Uses `method='nm'`.
- Supports fixed or render-time values for `n_steps`, `n_evals`, `simplex_size`, `tol_simplex`, `pars_init_method`, and `results_output_mode`.
- Accepts `add_path_dirs=...` for folders added to the MATLAB path before option initialization.
- Accepts `extra_options=...` for additional typed `estim_options(...)` calls appended after built-in algorithm options.
- Accepts `post_estimation_sections=...` for sections rendered after the `estim_pars` call.
- Uses `SavePredictionsSection()` as the default post-estimation section when `save_predictions=True`.

`RestartingNelderMead`

- Uses `method='nm'` for the initial optimizer run.
- Supports fixed or render-time values for the same initial optimizer options as `NelderMead`, except `results_output` is forced to `0` before estimation.
- Adds restart settings `n_runs`, `tol_restart`, and `results_output_mode`.
- Counts `n_runs` as optimizer calls only: the first `estim_pars` call plus restart-loop calls.
- Uses `tol_restart` to decide whether the objective value improved enough to continue restarting.
- Uses `GetResultsSection` for the final `method='no'` result-output call; this save call is not counted in `n_runs`.

`AlternatingRestartNelderMead`

- Inherits the restart settings and result-saving behavior from `RestartingNelderMead`.
- Renders `simplex_size` as a global MATLAB variable so it can be changed during the run script.
- Flips simplex direction with `simplex_size = -simplex_size;` before each restart attempt.
- Leaves the first optimizer call on the initial simplex direction.

Examples:

```python
from DEBtoolPyIF.estimation_files import (
    AlternatingRestartNelderMead,
    NelderMead,
    RestartingNelderMead,
    SetFilterOption,
)
from DEBtoolPyIF.estimation_files.run_sections import SavePredictionsSection

# n_steps is fixed; omitted values such as tol_simplex are read from estimation_settings.
run_template = NelderMead(
    n_steps=500,
    extra_options=(SetFilterOption(1),),
)

run_template = NelderMead(
    add_path_dirs=("data_pipeline", "ode"),
    n_steps=500,
)

# Replace the default post-estimation sections explicitly.
run_template = NelderMead(
    save_predictions=False,
    post_estimation_sections=(SavePredictionsSection(),),
)

run_template = RestartingNelderMead(
    n_steps=500,
    n_runs=5,
    tol_restart=1e-5,
    results_output_mode=0,
)

run_template = AlternatingRestartNelderMead(
    n_steps=500,
    simplex_size=0.05,
    n_runs=5,
    tol_restart=1e-5,
    results_output_mode=0,
)
```

High-level algorithm templates intentionally expose path additions, option customization, and post-estimation sections. If a workflow needs arbitrary section insertion between setup, option initialization, and the estimation call, compose `RunSection` objects directly with `RunProgrammaticTemplate`.

Source-backed run templates still work, but their placeholders must match registered section keys. For the base run contract, use `$setup`, `$set_options`, and `$estimation_call`. Do not use `$algorithm` as a required base placeholder.

### Automatic section registries

`MyDataSection`, `ParsInitSection`, and `RunSection` subclasses self-register when the class is defined.

Registration is opt-in:

- a section class must define `template_families = (...)` directly on the subclass
- a registered section must define a non-empty string `key`
- `section_tags = (...)` is optional and is used for grouped retrieval helpers

Only imported section classes are registered. If a project defines custom section classes in its own module, that module must be imported before constructing the templates that should discover those sections.

Inherited `template_families` do not opt a subclass into registration by themselves. A subclass that should register must set `template_families` directly in its class body.

Registry-backed templates do not maintain handwritten global lists of allowed section keys. For `mydata`:

- `MyDataTemplate.template_families = ("mydata",)`
- `MultitierMyDataTemplate.template_families = ("mydata", "multitier_mydata")`
- `available_section_classes()` asks the registry for all section classes in those families
- `allowed_section_keys()` is derived from the registered classes
- `section_classes_for_tag(tag)` and `sections_for_tag(tag)` select registered classes by tag

For `pars_init`:

- `ParsInitTemplate.template_families = ("pars_init",)`
- `MultitierParsInitTemplate.template_families = ("pars_init", "multitier_pars_init")`
- `allowed_section_keys()` is derived from the registered `ParsInitSection` classes
- `section_classes_for_tag(tag)` and `sections_for_tag(tag)` select registered classes by tag

The family list also defines override precedence. If a template family asks for more than one family, later families can replace earlier classes with the same key. This is how a multitier-specific section can specialize a generic `mydata` block while preserving the same placeholder key.

For example, `MultitierMyDataTemplate` reads both `mydata` and `multitier_mydata`. A class registered in `multitier_mydata` with the same key as a generic class can become the effective class for that key in the multitier template family.

### Registry-backed tags

Tags are not validation rules. They are grouping metadata used by template helpers.

Current important tags include:

- `data`
  - used by `MyDataTemplate.data_sections()`
- `tier_variables`
  - used by `MultitierMyDataTemplate.tier_variable_sections()`
- `metadata`
- `temperature`
- `weights`
- `pseudodata`
- `packing`
- `extra_info`
- `parameters`
- `chemistry`
- `tier_parameters`

`sections_for_tag(tag)` instantiates matching section classes with no arguments. Any section intended to be returned by these helpers must therefore be safe to instantiate with no required constructor arguments.

### Generic `mydata` sections

The generic `mydata` family is assembled from sections such as:

- metadata sections
- entity and group data sections
- extra-info sections
- weight sections
- pseudo-data sections
- packing sections
- temperature sections

Representative generic sections include:

- `MyDataFunctionHeaderSection`
- `SpeciesInfoMetadataSection`
- `TypicalTemperatureSection`
- `CompletenessLevelSection`
- `EntityDataSection`
- `GroupDataSection`
- `EntityDataTypesSection`
- `GroupDataTypesSection`
- `EntityListSection`
- `GroupsOfEntitySection`
- `ExtraInfoSection`
- `InitializeWeightsSection`
- `RemoveDummyWeightsSection`
- `AddPseudoDataSection`
- `SaveDataFieldsByVariateTypeSection`
- `AuthorInfoMetadataSection`
- `PackingSection`

`EntityListSection` and `GroupsOfEntitySection` expose iteration metadata for workflows that build data from a `DataCollection`-style source. In generic `mydata` templates these sections render into an `info` struct, which is packed as `auxData.info` when present:

- `info.entity_list`
- `info.groups_of_entity`

### Multitier `mydata` sections

The multitier subclass extends the generic `mydata` family with hierarchy-aware sections:

- `MultitierEntityListSection`
- `TierEntitiesSection`
- `TierGroupsSection`
- `MultitierGroupsOfEntitySection`
- `TierSubtreeSection`
- `TierParsSection`
- `TierParInitValuesSection`
- `SetTypicalTemperatureForAllDatasetsSection`
- `MultitierPseudoDataSection`
- `MultitierPackingSection`

These sections are what make the multitier helper structures explicit in the rendered MATLAB output.

`MultitierEntityListSection` and `MultitierGroupsOfEntitySection` intentionally use the same placeholder keys as the generic sections, but render to `tiers` instead of `info`. The multitier template family includes both `"mydata"` and `"multitier_mydata"`, so registry precedence selects the explicitly named multitier variants for `$entity_list` and `$groups_of_entity`.

### Defining new `MyDataSection` classes

Use this behavior when adding a new reusable `mydata` section class.

1. Subclass `MyDataSection`.
2. Define a stable non-empty `key`.
3. Add `template_families` if the key should become available automatically.
4. Add `section_tags` if the section should be discoverable by tag helpers.
5. Make no-argument construction work if the section will be used by `sections_for_tag(...)`.
6. Implement `render(context, state)` directly, or set `matlab_code` and use `get_init_substitutions()` / `get_render_substitutions()`.

Minimal registered section:

```python
from DEBtoolPyIF.estimation_files.mydata_base import MyDataSection


class CustomMetadataSection(MyDataSection):
    key = "custom_metadata_block"
    template_families = ("mydata",)
    section_tags = ("metadata",)
    matlab_code = "metaData.custom_field = '${custom_value}';"

    def __init__(self, *, custom_value: str = "") -> None:
        self.custom_value = custom_value
        super().__init__()

    def get_init_substitutions(self) -> dict[str, str]:
        return {"custom_value": self.custom_value}
```

Use `template_families = ("mydata",)` when the section should be available to generic `mydata` templates and inherited by multitier templates.

Use `template_families = ("multitier_mydata",)` when the section should only be available to multitier `mydata` templates.

Use both families only when the same class should be registered independently for both families.

Duplicate keys are rejected within the same registered family at class-definition time. If a class omits `template_families`, it is not registered and does not add a new allowed key automatically.

Unregistered section classes are still useful for replacing an already-allowed key in a specific template instance. For example, a one-off section with `key = "metadata_block"` can replace the default metadata block because that key is already allowed by the registered generic metadata section.

### Defining new `ParsInitSection` classes

Use this behavior when adding a reusable `pars_init` section class.

1. Subclass `ParsInitSection`.
2. Define a stable non-empty `key`.
3. Add `template_families` if the key should become available automatically.
4. Add `section_tags` if the section should be discoverable by tag helpers.
5. Make no-argument construction work if the section will be used by `sections_for_tag(...)`.
6. Implement `render(context)` directly, or set `matlab_code` and use `get_init_substitutions()` / `get_render_substitutions()`.

Minimal registered section:

```python
from DEBtoolPyIF.estimation_files.pars_init_base import ParsInitSection


class CustomParsInitCommentSection(ParsInitSection):
    key = "custom_comment"
    template_families = ("pars_init",)
    section_tags = ("metadata",)
    matlab_code = "% custom pars_init note"
```

Use `template_families = ("pars_init",)` when the section should be available to generic `pars_init` templates and inherited by multitier templates.

Use `template_families = ("multitier_pars_init",)` when the section should only be available to multitier `pars_init` templates.

For chemical overrides, the built-in `ParsInitChemicalParametersSection` is the preferred helper. It renders only the explicitly supplied chemical values and is intended to be inserted after `ParsInitAddChemSection()` when a workflow needs to override the defaults established by MATLAB `addchem(...)`.

Example:

```python
from DEBtoolPyIF.estimation_files import ParsInitChemicalParametersSection, ParsInitProgrammaticTemplate
from DEBtoolPyIF.estimation_files.pars_init_sections import ParsInitAddChemSection
from DEBtoolPyIF.parameters import get_chemical_parameter_values_of

template = ParsInitProgrammaticTemplate(
    sections=(
        ...,
        ParsInitAddChemSection(),
        ParsInitChemicalParametersSection(
            chemical_parameter_values=(
                get_chemical_parameter_values_of(
                    "urea",
                    mu=518181,
                    n_C=1,
                    n_H=2.216,
                ),
            )
        ),
        ...,
    )
)
```

For source-backed templates, add `$chemical_parameters` to the MATLAB source and pass the same section explicitly. This section is opt-in; the default registry-backed `pars_init` builders do not include it automatically.

### Required sections vs default sections

Each family distinguishes between:

- required sections, which must be present for the file contract to be valid
- default sections, which are the package-provided standard composition for that family

For `MultitierMyDataTemplate`, the required set includes the sections that define:

- the function header
- metadata
- entity and group data blocks
- the estimation entity list
- tier hierarchy helper structs
- tier parameter names and inherited initialization values
- weights
- pseudo-data
- final packing

Optional sections, such as additional metadata partitions or bibliography comments, can be added on top of that required contract.

### Placeholder matching in substitution templates

`SubstitutionTemplate` subclasses only render the sections referenced by the source template.

For example, a source-backed `mydata` template containing:

```matlab
$function_header
$entity_data_block
$packing_block
```

will only bind and render the sections whose keys match those placeholders.

This has two practical consequences:

- the MATLAB source template stays readable and controls file layout
- Python-side customization stays local to the placeholders the source actually uses

## Context And State Interfaces

The render pipeline is intentionally split into render context and derived render state.

### `GenerationContext`

`GenerationContext` is the base render context shared by all estimation-template families.

Current core fields:

- `species_name`
- `output_folder`

This base context is intentionally minimal.

### `MultitierGenerationContext`

`MultitierGenerationContext` is the multitier adapter used during actual estimation.

Important exposed values include:

- `tier_estimator`
- `tier_name`
- `entity_list`
- `pseudo_data_weight`
- `estimation_settings`
- `tier_pars`
- `extra_info`
- `full_pars_dict`
- `tier_par_init_values`

These properties are what connect template rendering to the current tier, the current estimation target, and the already-estimated tiers above it.

### `BaseMyDataState`

`BaseMyDataState` is the derived state consumed by generic `mydata` sections.

It collects shared render-ready values such as:

- entity data blocks
- group data blocks
- entity data types
- group data types
- `entity_list`
- `groups_of_entity`
- `extra_info`

### `MultitierMyDataState`

`MultitierMyDataState` extends `BaseMyDataState` with multitier-specific derived values:

- `tier_entities`
- `tier_groups`
- `tier_subtree`
- `tier_pars`
- `tier_par_init_values`

### State builders

`build_mydata_state(...)`

- builds generic `mydata` state directly from the render context

`build_multitier_mydata_state(...)`

- derives multitier helper structures by walking the tier hierarchy, collecting tier data, mapping descendants, and carrying inherited tier parameter values into render-ready form

## Data Flow For One Estimation Target

For one tier estimation target, the current flow is:

1. `TierEstimator.estimate(...)` resolves the current target entity list or group entity list.
2. It builds `MultitierGenerationContext.from_tier_estimator(...)`.
3. `write_tier_estimation_files(...)` iterates over the tier's four template objects.
4. `mydata` templates build derived state and render section content from both context and state.
5. `pars_init` and `run` templates render their registered sections directly from the context.
6. `predict` is copied or rendered according to its template strategy.
7. The writer stores the final MATLAB files in the current output folder.

This means the tier estimator owns target selection, the generation context owns render inputs, and the template classes own how those inputs become concrete MATLAB code.

## Canonical User Pattern

The preferred workflow is to construct templates explicitly in Python and pass them into `MultiTierStructure` as `estimation_templates`.

High-level pattern:

```python
from DEBtoolPyIF import MultiTierStructure
from DEBtoolPyIF.estimation_files import EstimationTemplates, CopyFileTemplate
from DEBtoolPyIF.estimation_files.algorithms import NelderMead
from DEBtoolPyIF.multitier import (
    MultitierMyDataSubstitutionTemplate,
    RegistryMultitierParsInitProgrammaticTemplate,
)

estimation_templates = {
    "diet": EstimationTemplates(
        mydata=MultitierMyDataSubstitutionTemplate(...),
        pars_init=RegistryMultitierParsInitProgrammaticTemplate(...),
        predict=CopyFileTemplate(...),
        run=NelderMead(),
    ),
}

multitier = MultiTierStructure(
    ...,
    estimation_templates=estimation_templates,
)
```

The updated Angus example is the canonical reference for this workflow.

## Relationship To The Other Docs

- [MULTITIER_WORKFLOW.md](MULTITIER_WORKFLOW.md)
  - use for the recommended project layout and user workflow
- [DEBTOOL_FILES.md](DEBTOOL_FILES.md)
  - use for the general MATLAB species-file contract
- [DEBTOOL_MULTITIER.md](DEBTOOL_MULTITIER.md)
  - use for the helper-structure contract inside multitier DEBtool files
- [MULTITIER.md](MULTITIER.md)
  - use for the broader methodology and implementation architecture
