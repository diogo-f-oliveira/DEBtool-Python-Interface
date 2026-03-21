import numpy as np
import pytest

from DEBtoolPyIF.utils.data_conversion import (
    convert_dict_to_matlab,
    convert_list_of_strings_to_matlab,
    convert_numeric_array_to_matlab,
    convert_string_to_matlab,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("kg", "'kg'"),
        ("", "''"),
    ],
)
def test_convert_string_to_matlab(value, expected):
    assert convert_string_to_matlab(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (5, 5),
        (3.2, 3.2),
        (np.array(7), 7),
        (np.array([[0, 1], [2, 3]]), "[0 1; 2 3]"),
        (np.array([[1.5, 2.0]]), "[1.5 2.0]"),
        (np.array([[1], [2]]), "[1; 2]"),
    ],
)
def test_convert_numeric_array_to_matlab_supported_shapes(value, expected):
    assert convert_numeric_array_to_matlab(value) == expected


@pytest.mark.parametrize(
    ("value", "double_brackets", "expected"),
    [
        (["a", "b"], False, "{'a', 'b'}"),
        ([], False, "{}"),
        (["Pen_2"], True, "{{'Pen_2'}}"),
    ],
)
def test_convert_list_of_strings_to_matlab(value, double_brackets, expected):
    assert convert_list_of_strings_to_matlab(value, double_brackets=double_brackets) == expected


@pytest.mark.parametrize(
    ("value", "is_string_data", "expected"),
    [
        ({}, False, "struct()"),
        ({"PT1": 507, "PT2": 545}, False, "struct('PT1', 507, 'PT2', 545)"),
        (
            {"individual": "{{'Pen_2'}}"},
            False,
            "struct('individual', {{'Pen_2'}})",
        ),
        (
            {"species": "Bos_taurus_Angus"},
            True,
            "struct('species', 'Bos_taurus_Angus')",
        ),
    ],
)
def test_convert_dict_to_matlab(value, is_string_data, expected):
    assert convert_dict_to_matlab(value, is_string_data=is_string_data) == expected


def test_convert_dict_to_matlab_preserves_insertion_order():
    data = {"second": 2, "first": 1, "third": 3}

    assert (
        convert_dict_to_matlab(data)
        == "struct('second', 2, 'first', 1, 'third', 3)"
    )


def test_group_initial_weights_contract_matches_group_datasource_usage():
    initial_weights = {"PT1": 507, "PT2": 545}

    assert (
        convert_dict_to_matlab(initial_weights)
        == "struct('PT1', 507, 'PT2', 545)"
    )


def test_multitier_nested_struct_contract_matches_mydata_generation_usage():
    tier_groups = {
        "diet": convert_list_of_strings_to_matlab([], double_brackets=True),
        "individual": convert_list_of_strings_to_matlab(["Pen_2"], double_brackets=True),
    }
    groups_of_entity = {
        "PT1": convert_list_of_strings_to_matlab(["Pen_2"], double_brackets=True),
        "PT2": convert_list_of_strings_to_matlab(["Pen_2", "Pen_5"], double_brackets=True),
    }
    tier_par_init_values = {
        "p_Am": convert_dict_to_matlab({"PT1": 1.1, "PT2": 2.2}),
        "kap_X": convert_dict_to_matlab({"PT1": 0.3, "PT2": 0.4}),
    }

    assert (
        convert_dict_to_matlab(tier_groups)
        == "struct('diet', {{}}, 'individual', {{'Pen_2'}})"
    )
    assert (
        convert_dict_to_matlab(groups_of_entity)
        == "struct('PT1', {{'Pen_2'}}, 'PT2', {{'Pen_2', 'Pen_5'}})"
    )
    # Nested struct values are expected to be pre-converted by callers and inserted verbatim.
    assert (
        convert_dict_to_matlab(tier_par_init_values)
        == "struct('p_Am', struct('PT1', 1.1, 'PT2', 2.2), 'kap_X', struct('PT1', 0.3, 'PT2', 0.4))"
    )
