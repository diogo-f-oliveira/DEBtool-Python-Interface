"""Generic estimation-file generation interfaces and helpers."""

from .config import EstimationTemplates, FILE_KEYS, normalize_estimation_templates
from .mydata import (
    MyDataSection,
    MyDataProgrammaticTemplate,
    MyDataSubstitutionTemplate,
    build_mydata_state,
    build_mydata_substitutions,
)
from .mydata_base import BaseMyDataState
from .pars_init import (
    ParsInitProgrammaticTemplate,
    ParsInitSubstitutionTemplate,
    RegistryParsInitProgrammaticTemplate,
    RegistryParsInitSubstitutionTemplate,
)
from .pars_init_base import ParsInitSection
from .pars_init_sections import ParsInitChemicalParametersSection, ParsInitReferenceTemperatureSection
from .run import (
    RunProgrammaticTemplate,
    RunSubstitutionTemplate,
)
from .run_options import (
    EstimOption,
    SetEstimOptionsSection,
    IntegerEstimOption,
    NumericEstimOption,
    RunSetting,
    SetDefaultEstimOptions,
    SetFilterOption,
    SetMaxFunEvalsOption,
    SetMaxStepNumberOption,
    SetMethodOption,
    SetParsInitMethodOption,
    SetResultsOutputOption,
    SetSimplexSizeOption,
    SetTolSimplexOption,
    StringEstimOption,
)
from .run_sections import AddPathSection, RunSection
from .algorithms import AlgorithmRunTemplate, AlternatingRestartNelderMead, NelderMead, RestartingNelderMead
from .templates import (
    CopyFileTemplate,
    EstimationFileSection,
    EstimationFileTemplate,
    ProgrammaticTemplate,
    SubstitutionTemplate,
)

__all__ = [
    "EstimationFileSection",
    "FILE_KEYS",
    "EstimationTemplates",
    "CopyFileTemplate",
    "EstimationFileTemplate",
    "ProgrammaticTemplate",
    "SubstitutionTemplate",
    "BaseMyDataState",
    "MyDataSection",
    "MyDataProgrammaticTemplate",
    "MyDataSubstitutionTemplate",
    "ParsInitProgrammaticTemplate",
    "ParsInitSubstitutionTemplate",
    "RegistryParsInitProgrammaticTemplate",
    "RegistryParsInitSubstitutionTemplate",
    "ParsInitSection",
    "ParsInitChemicalParametersSection",
    "ParsInitReferenceTemperatureSection",
    "AddPathSection",
    "RunSection",
    "RunSetting",
    "EstimOption",
    "NumericEstimOption",
    "IntegerEstimOption",
    "StringEstimOption",
    "SetDefaultEstimOptions",
    "SetEstimOptionsSection",
    "SetMaxStepNumberOption",
    "SetMaxFunEvalsOption",
    "SetSimplexSizeOption",
    "SetFilterOption",
    "SetTolSimplexOption",
    "SetParsInitMethodOption",
    "SetResultsOutputOption",
    "SetMethodOption",
    "RunProgrammaticTemplate",
    "RunSubstitutionTemplate",
    "AlgorithmRunTemplate",
    "NelderMead",
    "RestartingNelderMead",
    "AlternatingRestartNelderMead",
    "build_mydata_state",
    "build_mydata_substitutions",
    "normalize_estimation_templates",
]
