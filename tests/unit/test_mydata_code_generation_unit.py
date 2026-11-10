import pytest

from DEBtoolPyIF.utils.mydata_code_generation import (
    generate_struct_variable_code,
    generate_tier_variable_code,
    is_valid_matlab_field_name,
    sanitize_matlab_field_name,
)


@pytest.mark.parametrize(
    ("field_name", "expected"),
    [
        ("PT1", True),
        ("field_name", True),
        ("PT 1", False),
        ("123field", False),
        ("field-name", False),
        ("", False),
    ],
)
def test_is_valid_matlab_field_name(field_name, expected):
    assert is_valid_matlab_field_name(field_name) is expected


@pytest.mark.parametrize(
    ("field_name", "expected"),
    [
        ("PT1", "PT1"),
        ("PT 1", "PT_1"),
        ("field-name", "field_name"),
        ("123field", "x123field"),
        ("", "x"),
    ],
)
def test_sanitize_matlab_field_name(field_name, expected):
    sanitized = sanitize_matlab_field_name(field_name)

    assert sanitized == expected
    assert is_valid_matlab_field_name(sanitized)


def test_generate_struct_variable_code_targets_requested_struct():
    rendered = generate_struct_variable_code(
        var_name="entity_list",
        converted_data="{'entity_1'}",
        struct_name="info",
        label="List of entities",
    )

    assert "data.entity_list = 10;" in rendered
    assert "info.entity_list = {'entity_1'};" in rendered
    assert "units.info.entity_list = '-';" in rendered
    assert "label.info.entity_list = 'List of entities';" in rendered
    assert "tiers.entity_list" not in rendered


def test_generate_tier_variable_code_preserves_tiers_wrapper():
    rendered = generate_tier_variable_code(
        var_name="entity_list",
        converted_data="{'entity_1'}",
        label="List of entities",
        pars_init_access=True,
    )

    assert "tiers.entity_list = {'entity_1'};" in rendered
    assert "metaData.entity_list = tiers.entity_list;" in rendered
