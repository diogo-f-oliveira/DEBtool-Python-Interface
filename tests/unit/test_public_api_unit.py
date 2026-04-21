import DEBtoolPyIF
import DEBtoolPyIF.estimation_files as estimation_files
import DEBtoolPyIF.multitier as multitier

from DEBtoolPyIF import (
    DEBModelParametrizationProblem,
    DataCollection,
    EstimationRunner,
    get_parameter_registry_of_typified_model,
    MATLABWrapper,
    MultiTierStructure,
    ParameterDefinition,
    ParameterRegistry,
    TierEstimator,
    TierHierarchy,
    TierHierarchyError,
)
from DEBtoolPyIF.parameters import StdParameterRegistry, StxParameterRegistry, p_Am
from DEBtoolPyIF.data_sources import (
    AgeWeightTwinsEntityDataSource,
    DataSourceBase,
    DigestibilityEntityDataSource,
    EntityDataSourceBase,
    GroupDataSourceBase,
    TimeCH4EntityDataSource,
    TimeCO2EntityDataSource,
    TimeFeedGroupDataSource,
    TimeMilkEntityDataSource,
    TimeWeightEntityDataSource,
    WeightEntityDataSource,
    ZeroVariateEntityDataSource,
    ZeroVariateGroupDataSourceBase,
)
from DEBtoolPyIF.estimation import (
    DEBModelParametrizationProblem as EstimationProblemFromSubpackage,
    DEBtoolWrapper,
    EstimationRunner as EstimationRunnerFromSubpackage,
    MATLABWrapper as MATLABWrapperFromSubpackage,
)
from DEBtoolPyIF.multitier import (
    MultiTierStructure as MultiTierStructureFromSubpackage,
    TierEstimator as TierEstimatorFromSubpackage,
    TierHierarchy as TierHierarchyFromSubpackage,
    TierHierarchyError as TierHierarchyErrorFromSubpackage,
)
from DEBtoolPyIF.notebook import TierVisualizer


def test_root_public_api_exports_expected_symbols():
    assert DataCollection.__name__ == "DataCollection"
    assert TierHierarchy.__name__ == "TierHierarchy"
    assert TierHierarchyError.__name__ == "TierHierarchyError"
    assert MultiTierStructure.__name__ == "MultiTierStructure"
    assert TierEstimator.__name__ == "TierEstimator"
    assert MATLABWrapper.__name__ == "MATLABWrapper"
    assert EstimationRunner.__name__ == "EstimationRunner"
    assert DEBModelParametrizationProblem.__name__ == "DEBModelParametrizationProblem"
    assert ParameterDefinition.__name__ == "ParameterDefinition"
    assert ParameterRegistry.__name__ == "ParameterRegistry"
    assert get_parameter_registry_of_typified_model.__name__ == "get_parameter_registry_of_typified_model"
    assert p_Am.name == "p_Am"


def test_root_public_api_does_not_export_typified_registry_classes():
    assert not hasattr(DEBtoolPyIF, "StdParameterRegistry")
    assert not hasattr(DEBtoolPyIF, "StxParameterRegistry")
    assert hasattr(DEBtoolPyIF, "get_parameter_registry_of_typified_model")


def test_subpackage_public_api_exports_expected_symbols():
    exported_data_source_classes = {
        DataSourceBase,
        EntityDataSourceBase,
        GroupDataSourceBase,
        ZeroVariateEntityDataSource,
        ZeroVariateGroupDataSourceBase,
        TimeWeightEntityDataSource,
        WeightEntityDataSource,
        TimeCH4EntityDataSource,
        TimeCO2EntityDataSource,
        TimeMilkEntityDataSource,
        AgeWeightTwinsEntityDataSource,
        DigestibilityEntityDataSource,
        TimeFeedGroupDataSource,
    }

    assert len(exported_data_source_classes) == 13
    assert MATLABWrapperFromSubpackage is MATLABWrapper
    assert EstimationRunnerFromSubpackage is EstimationRunner
    assert EstimationProblemFromSubpackage is DEBModelParametrizationProblem
    assert issubclass(DEBtoolWrapper, MATLABWrapper)
    assert TierHierarchyFromSubpackage is TierHierarchy
    assert TierHierarchyErrorFromSubpackage is TierHierarchyError
    assert MultiTierStructureFromSubpackage is MultiTierStructure
    assert TierEstimatorFromSubpackage is TierEstimator
    assert TierVisualizer.__name__ == "TierVisualizer"
    assert StdParameterRegistry.__name__ == "StdParameterRegistry"
    assert StxParameterRegistry.__name__ == "StxParameterRegistry"


def test_root_exported_hierarchy_types_work_without_matlab():
    hierarchy = TierHierarchy.from_paths(
        tier_names=["breed", "diet", "individual"],
        paths=[
            {"breed": "male", "diet": "CTRL", "individual": "PT1"},
            {"breed": "male", "diet": "TMR", "individual": "PT2"},
        ],
    )

    assert hierarchy.root_tier == "breed"
    assert hierarchy.get_entities("diet") == ("CTRL", "TMR")
    assert hierarchy.get_parent("diet", "CTRL") == "male"


def test_multitier_template_exports_follow_package_ownership():
    assert hasattr(multitier, "MultitierMyDataProgrammaticTemplate")
    assert hasattr(multitier, "MultitierMyDataSubstitutionTemplate")
    assert hasattr(multitier, "MultitierParsInitProgrammaticTemplate")
    assert hasattr(multitier, "MultitierParsInitSubstitutionTemplate")
    assert hasattr(multitier, "RegistryMultitierParsInitProgrammaticTemplate")
    assert hasattr(DEBtoolPyIF, "RegistryMultitierParsInitProgrammaticTemplate")
    assert not hasattr(DEBtoolPyIF, "TierEstimationFiles")
    assert not hasattr(estimation_files, "TierEstimationFiles")
    assert not hasattr(estimation_files, "MultitierMyDataProgrammaticTemplate")
    assert not hasattr(estimation_files, "MultitierMyDataSubstitutionTemplate")
    assert not hasattr(estimation_files, "MultitierParsInitProgrammaticTemplate")
    assert not hasattr(estimation_files, "MultitierParsInitSubstitutionTemplate")
