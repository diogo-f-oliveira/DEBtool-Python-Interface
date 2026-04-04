# DEBtoolPyIF Development Plan

This document captures the current development direction for `DEBtoolPyIF` based on the present package state, the multitier methodology paper, and project priorities discussed after reviewing the codebase.

The package is still pre-1.0. The main goal is to make the multitier workflow reliable, easier to use, and broad enough to support a near-term major release without breaking the current example-driven workflow.

## Guiding Priorities

- Preserve compatibility with the existing multitier workflow and example structure unless a deliberate interface change is made.
- Prioritize reliability, clear APIs, and reproducible estimation outputs over experimental methodology extensions.
- Focus first on features that improve estimation quality and make multitier estimation easier to inspect and iterate on.
- Treat more advanced statistical extensions as future work unless they directly support the core package workflow.

## Immediate Priorities

These are the highest-priority items to add.

### 1. Better documentation and examples for the multitier workflow

The package currently has some documentation and examples, but they are still limited and example-oriented. Improving the documentation and examples should be a top priority to make the multitier workflow more accessible to users. This includes:

- [ ] Improving the description of the example on Bos taurus Angus with at least a README file in the example folder that explains the workflow and how to run it.
- [x] Writing a document explaining the overall logic of AmP estimation, which will be useful for both agents and users
- [x] Writing a document explaining the multitier estimation methodology and the steps involved in the workflow, including how to define data sources, create tier structures, and run estimations. This document should also point to the relevant code and examples in the package to help users understand how to use the package effectively.
- [x] Adding comments in the generic template files to explain the purpose of each section and how it relates to the multitier estimation process, making it easier for users to understand and modify the templates as needed.
- [ ] Providing more examples that cover different types of data sources, tier structures, and estimation scenarios to help users see how the package can be applied to a variety of use cases.

### 2. Integration tests with generic multitier estimation template files

We have updated the generic template files to cover all multiter estimation steps. We should leverage these templates to create integration tests that run through the full multitier estimation workflow using generated data and parameters. This will help ensure that the core workflow is reliable and that changes to the package do not break the expected estimation process. Examples are still useful, but the generic templates allow us to test edge cases in multitier formulations. Steps to achieve this include:

- Create integration tests that use the generic template files to run through the full multitier estimation workflow, including data loading, tier structure creation, and estimation.
- Use generated data and parameters in the tests to cover a variety of scenarios and edge cases in multitier estimation.
- Ensure that the tests check for expected outputs and that any changes to the package do not break the core estimation workflow.
- Update the test suite to include these integration tests and run them regularly to maintain confidence in the package's reliability.

## Important Improvements To Existing Functionality

These areas are already implemented in some form, but should be improved to make the package more capable and easier to maintain.

### 1. Better Control over Dataset Weights

The current implementation of dataset weighting is basic and does not allow for fine-grained control over how different datasets contribute to the estimation process. It depends solely on the user to create code in the template files to set dataset weights. This should be simplified and made more flexible by:

- Adding capabilities to specify dataset weights directly in the Python API, with sensible defaults.
- Update generic template files to include logic for applying these weights without requiring users to write custom code in the templates.
- Providing clearer documentation and examples on how to use dataset weights effectively in multitier estimation.

### 2. Richer Pseudo-Data And Constraint Handling

Pseudo-data inheritance is already implemented, but the current interface is still narrow.

Future improvements should include:

- better control of pseudo-data weights,
- easier overrides for specific entities or parameters,
- clearer APIs for tier-to-tier anchoring,
- groundwork for later uncertainty-aware constraints if needed.

### 3. Better Data-Source Automation And Generation

The package still needs more work on data sources and on how their generation is automated.

This should be one of the next priorities after adding more functionality for results. In particular, the package should move toward a clearer and more reliable workflow for:

- defining data sources,
- generating estimation-ready datasets from those sources,
- reducing manual wiring between Python-side data definitions and MATLAB estimation files,
- supporting a broader range of tier data setups without relying on ad hoc example-specific code.

This area matters both for usability and for correctness, because the data-source layer is the foundation of the generated multitier estimation inputs.

### 4. Automatic Data Conversion between Python and MATLAB

The package currently relies on users to ensure that data passed from Python to MATLAB is in the correct format, especially for numeric arrays. This can lead to issues with missing values, infinite values, or other special cases that need to be represented correctly in MATLAB. There are internal functions to handle most of this conversion, but they are not yet fully integrated into the user-facing API. Next steps would be to:

- Develop a more robust data conversion layer that automatically handles the conversion of Python data structures to MATLAB-compatible formats, including proper handling of `NaN`, `Inf`, and `-Inf` values.
- Integrate this conversion layer into the API so that users can pass data in native Python formats without worrying about MATLAB compatibility.
- Provide clear documentation and examples on how the data conversion works and how users can ensure their data is correctly formatted for MATLAB estimation.
- Update and improve the existing test suite to cover edge cases in data conversion, ensuring that the package can handle a wide range of input data without errors.

### 5. Automated `pars_init.m` Generation

The `pars_init.m` file is currently generated from a template created by the user. Parameter values are defined in code and are then filled by the template. Given the simple structure of the `pars_init.m` file, it should be possible to automate its generation based on the parameters defined in the Python code. This would reduce the amount of manual work required to set up the estimation and ensure that the `pars_init.m` file is always consistent with the parameters defined in Python. Steps to achieve this include:

- Define a clear structure for how parameters are defined in Python, including any necessary metadata such as parameter names, values, and sources. 
- Create classes to host estimated parameters and their metadata, which can be used to generate the `pars_init.m` file automatically.
- Core parameters should be defined in the package code, but base classes should be made available for users to define their own parameters as needed, with clear APIs for how to specify parameter values and metadata.
- Implement a function that takes the defined parameters and their metadata and generates the `pars_init.m` file in the correct format for MATLAB estimation.
- Update `pars_init.m` generation in `TierCodeGenerator`

### 6. Selective Reruns And Partial Tier Estimation

Partial tier estimation can now be requested by passing a subset of tier entities into `TierEstimator.estimate(...)`.
The current implementation resolves estimation targets conservatively:

- standalone requested entities are estimated on their own,
- requested entities that belong to a group expand to the full group estimation target,
- the user receives a warning listing the additional entities that must be estimated with that group.

This is an intentional interim behavior. Truly estimating only a subset of entities within a grouped run requires updating the generated MATLAB templates so shared group data can be included, but the estimation logic only runs for the requested entities. This requires fixing the parameters of non-estimated entries. Implementation steps would be:

- Improve functionality of `TierEstimator.estimate(...)` to allow users to specify which entities to estimate while ensuring that the necessary data for those entities is still included in the estimation process.
- Update `TierCodeGenerator` to generate list of parameters estimated for each entity.
- Add logic to the estimation process to fix parameters of non-estimated entities based on the generated list, ensuring that the estimation runs correctly even when only a subset of entities is being estimated.
- Update metadata reporting to clearly indicate which entities were estimated and which were fixed, along with the rationale for any fixed parameters.
- Provide clear documentation and examples on how to use selective reruns and partial tier estimation effectively, including any limitations or considerations users should be aware of when using this feature.

### 7. Better Visualization And Comparison Tooling

The package has notebook visualization utilities, but they are still limited and example-oriented.

Useful next improvements include:

- better comparison views across runs,
- parameter distribution plots,
- tier-to-tier deviation summaries,
- candidate ranking dashboards,
- cleaner figure generation for paper-style analysis.

### 8. Evaluate how extra info should be incorporated into multitier estimation

Currently, the package supports a simple form of extra information in the estimation for code not based on DataSource classes but that users want to generate programmatically. This is done by allowing users to pass a dictionary of extra info to the `estimate` method of `TierEstimator`, which is then passed to the MATLAB templates for use in estimation. This should be replace by a more structured version which includes metadata saving and better integration with the rest of the package. Next steps include:

- Define a clear structure for the extra information that can be passed to the estimation process, including what types of information are expected and how they should be formatted.
- Store both raw and converted versions of the extra information in the estimation results for reproducibility and easier inspection.
- Design guidelines for users to prefer using custom DataSource classes for defining extra information when possible, and provide clear documentation and examples on how to do this effectively.


## Future Pipeline

These items are desirable, but not current core priorities.

### 1. Data-source classes for zero-variate species data

Species zero-variate data are currently handled by hardcoded template content. This should be moved toward a more uniform data-source class that can be used for both individual and species-level data, with clearer APIs for defining and generating zero-variate datasets. This would help make the top-tier data handling feel more integrated into the Python package API and reduce reliance on handwritten MATLAB templates for species-level data. Steps to achieve this include:

- Defining a new data-source simplified class specifically for zero-variate species data, with methods for specifying the data and its associated metadata including sources.
- Creating a specific DataCollection subclass for species-level data that can handle zero-variate datasets and integrate with the existing multitier structure or future species estimation pipelines.
- Updating the template generation logic to use this new data-source class for species-level data, ensuring that the generated MATLAB files correctly reflect the data defined in Python.
- Providing documentation and examples on how to use the new data-source class for species-level data, including how to define zero-variate datasets and how they fit into the overall estimation workflow.

### 2. Simultaneous Estimation Formulations

The paper discusses simultaneous estimation as an alternative formulation, but the package currently implements only the sequential multitier approach.

Support for simultaneous estimation would be useful in the future, but it is not a short-term priority. The current focus should remain on making the sequential multitier workflow strong and ergonomic.

### 3. Automated `run.m` generation for different optimization algorithms

Generation for `run.m` files is currently handwritten in the example templates. This file is rather easy to generate and automate its generation since the commands are very similar. Moreover, we can define different run.m files that implement different optimization algorithms, namely: Nelder-Mead, Restarting Nelder-Mead, and Restarting Alternating Nelder-Mead or even the MultiCalib4DEB work. Steps to achieve this include:

- Define a clear structure for the `run.m` file, including the necessary commands and parameters for running the estimation process.
- Decide on the architectural approach for generating `run.m` files, such as using a template-based approach or a more programmatic generation method based on the defined structure.
- Create classes or functions that can generate `run.m` files based on the defined structure, allowing for different optimization algorithms to be implemented as needed.
- Implement each optimization algorithm as a separate generation option, ensuring that the generated `run.m` files are correctly formatted and include all necessary commands and options for the chosen algorithm.
- Update the generation logic in `TierCodeGenerator` to use this new `run.m` generation functionality, ensuring that the correct `run.m` file is generated based on user preferences or defaults.

### 4. Automated `mydata.m` generation

The `mydata.m` file is currently generated from a template created by the user. Given the structure of the `mydata.m` file, it should be possible to automate its generation based on the data sources defined in Python and species metadata defined by the user. This would reduce the amount of manual work required to set up the estimation and ensure that the `mydata.m` file is always consistent with the data sources and species metadata defined in Python. Steps to achieve this include:

- Define a clear structure for how data sources and species metadata are defined in Python, including any necessary metadata such as data source names, values, and sources.
- Decide on architectural approach for generating `mydata.m` files, such as using a template-based approach or a more programmatic generation method based on the defined structure.
- Create classes or functions that can generate `mydata.m` files based on the defined structure, ensuring that the generated file correctly reflects the data sources and species metadata defined in Python.
- Integrate with `DataSource` classes to automatically generate the necessary data definitions in the `mydata.m` file based on the data sources defined in Python.
- Update the generation logic in `TierCodeGenerator` to use this new `mydata.m` generation functionality, ensuring that the correct `mydata.m` file is generated based on the defined data sources and species metadata.
- Provide documentation and examples on how to use the new `mydata.m` generation functionality, including how to define data sources and species metadata in Python and how they are reflected in the generated `mydata.m` file.
- Maintain backwards compatibility with existing `mydata.m` templates that are completely handwritten with template arguments through a freeform generation class. 


## Future Minor Versions

These are planned directions for future minor releases, but not immediate priorities for the core multitier workflow.

### 1. Automated Parameter-Set Search And Comparison

The package currently requires `tier_pars` to be chosen manually before running the workflow. The paper, however, relies heavily on comparing alternative trial-level and individual-level parameter choices and then selecting among them using fit quality and biological plausibility.

This should be added in a future minor version rather than in the immediate development phase.

The package should eventually gain first-class support for:

- defining candidate parameter subsets for one or more tiers,
- running batch experiments over those combinations,
- collecting results in a uniform format,
- ranking or filtering candidates,
- making it easy to compare tradeoffs across candidate tier parameterizations.

### 2. More Complete Species Estimation File Generation

A future minor version should improve support for generating species estimation files more systematically.

This includes moving toward a cleaner and more uniform workflow for higher-tier and species-level datasets, instead of relying on hardcoded template content where possible.

This work should help make top-tier data handling feel like part of the Python package API, not only part of handwritten MATLAB templates.

### 3. Higher-Level Abstractions For `predict` Logic

The current template-based approach works well, but `predict` files still require a lot of tier-specific MATLAB logic.

This should be treated as future minor-version work. The goal is to reduce repeated hierarchy boilerplate by adding clearer abstractions or reusable generation patterns for common multitier structures.

### 4. Add-my-Pet Integration

Future minor versions should add functionality to work with Add-my-Pet.

Planned directions include:

- fetching species files,
- fetching parameter sets,
- using Add-my-Pet material as initialization or reference data,
- generating datasets or estimation inputs from Add-my-Pet resources,
- making it easier to bootstrap species workflows from existing Add-my-Pet content.

This should eventually connect the package's multitier workflow with the broader DEB ecosystem in a practical way.

### 5. Parallel Execution Of Independent Estimations

The package already separates estimations by independent tier groups or entities, but it currently runs them serially.

Support for parallel execution would be useful eventually where tiers contain independent runs, such as:

- multiple diets,
- multiple pens,
- many individuals,
- multiple candidate parameter combinations.

This is a long-term priority. It is harder to implement safely than several other improvements, so it should come late in the roadmap. When it is eventually added, it should be done carefully so the output structure remains deterministic and easy to inspect.

## Suggested Development Order

The current recommended order of work is:

1. better control over dataset weights,
2. richer pseudo-data and constraint handling,
3. better data-source automation and dataset generation,
4. automatic data conversion between Python and MATLAB,
5. automated `pars_init.m` generation,
6. selective reruns and partial tier estimation,
7. better visualization and comparison tooling,
8. evaluate how extra info should be incorporated into multitier estimation,
9. data-source classes for zero-variate species data,
10. simultaneous estimation formulations,

## Future minor-version work includes:
1. future minor-version work on automated parameter-set search, 
2. future minor-version work on species-file generation 
3. future minor version on `predict` code generation, 
4. future minor-version work on Add-my-Pet integration,
5. long-term work on parallel execution.


## Summary

The near-term direction for `DEBtoolPyIF` is to make multitier estimation easier to run as a serious workflow:

- better at producing strong results,
- easier to compare,
- easier to inspect,
- easier to rerun,
- easier to extend.

The package already contains the essential multitier execution machinery. The next phase is to turn that machinery into a fuller research and development workflow while keeping broader automation, ecosystem integrations, and harder execution features on a staged roadmap.
