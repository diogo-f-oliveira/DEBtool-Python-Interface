import pytest

from DEBtoolPyIF.multitier.procedure import MultiTierStructure


@pytest.mark.integration
def test_create_tier_structure_returns_multitier_structure(
    example_name, examples_root, import_example_data_module, import_example_tier_module
):
    data_module = import_example_data_module(example_name)
    tier_module = import_example_tier_module(example_name)

    assert hasattr(data_module, "load_data"), f"Missing load_data() in examples/{example_name}/data.py"
    assert hasattr(tier_module, "create_tier_structure"), (
        f"Missing create_tier_structure() in examples/{example_name}/tier_structure.py"
    )

    data = data_module.load_data(str(examples_root / example_name / "data"))
    tier_structure = tier_module.create_tier_structure(data, matlab_session="ignore")

    assert isinstance(tier_structure, MultiTierStructure)


@pytest.mark.integration
def test_create_tier_structure_has_core_multitier_attributes(
    example_name, examples_root, import_example_data_module, import_example_tier_module
):
    data_module = import_example_data_module(example_name)
    tier_module = import_example_tier_module(example_name)

    data = data_module.load_data(str(examples_root / example_name / "data"))
    tier_structure = tier_module.create_tier_structure(data, matlab_session="ignore")

    assert hasattr(tier_structure, "tier_names")
    assert hasattr(tier_structure, "tiers")
    assert isinstance(tier_structure.tiers, dict)
