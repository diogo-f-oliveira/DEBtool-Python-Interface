import pytest

from DEBtoolPyIF.utils.mydata_code_generation import (
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
