import numpy as np
import pytest

from DEBtoolPyIF.utils.data_conversion import (
    CONVERSION_INPUT_TYPE_MAP,
    _format_numeric_value,
    convert_dict_to_matlab,
    convert_list_of_strings_to_matlab,
    convert_numeric_array_to_matlab,
    convert_scalar_to_matlab,
    convert_string_or_collection_to_matlab,
    convert_string_to_matlab,
)


def test_conversion_input_type_map_documents_all_conversion_functions():
    assert CONVERSION_INPUT_TYPE_MAP == {
        "convert_string_to_matlab": {
            "string": "str",
        },
        "_format_numeric_value": {
            "value": "int | float | np.integer | np.floating",
            "format_code": "str | None",
        },
        "convert_numeric_array_to_matlab": {
            "array": "int | float | np.integer | np.floating | np.ndarray",
            "format_codes": "str | Sequence[str] | None",
        },
        "convert_scalar_to_matlab": {
            "value": "str | bool | np.bool_ | int | float | np.integer | np.floating",
        },
        "convert_list_of_strings_to_matlab": {
            "list_data": "list[str] | tuple[str, ...]",
            "double_brackets": "bool",
        },
        "convert_string_or_collection_to_matlab": {
            "value": "str | list[str] | tuple[str, ...]",
        },
        "convert_dict_to_matlab": {
            "dict_data": "dict[str, str | bool | np.bool_ | int | float | np.integer | np.floating]",
            "is_string_data": "bool",
        },
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("kg", "'kg'"),
        ("", "''"),
        ("O'Brien", "'O''Brien'"),
    ],
)
def test_convert_string_to_matlab(value, expected):
    assert convert_string_to_matlab(value) == expected


@pytest.mark.parametrize("value", [1, True, None, ["kg"]])
def test_convert_string_to_matlab_rejects_non_strings(value):
    with pytest.raises(TypeError, match="convert_string_to_matlab expected string"):
        convert_string_to_matlab(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("nm", "'nm'"),
        ("O'Brien", "'O''Brien'"),
        (True, "1"),
        (False, "0"),
        (np.bool_(True), "1"),
        (np.bool_(False), "0"),
        (5, "5"),
        (3.2, "3.2"),
        (np.int64(7), "7"),
        (np.float64(1.5), "1.5"),
        (np.nan, "NaN"),
        (np.inf, "Inf"),
        (-np.inf, "-Inf"),
    ],
)
def test_convert_scalar_to_matlab(value, expected):
    assert convert_scalar_to_matlab(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        [1],
        {"value": 1},
        np.array(1),
        1 + 2j,
        np.complex64(1 + 2j),
    ],
)
def test_convert_scalar_to_matlab_rejects_invalid_scalars(value):
    with pytest.raises(TypeError, match="convert_scalar_to_matlab expected value"):
        convert_scalar_to_matlab(value)


def test_format_numeric_value_validates_value_type():
    with pytest.raises(TypeError, match="_format_numeric_value expected value"):
        _format_numeric_value(True)


def test_format_numeric_value_validates_format_code_type():
    with pytest.raises(TypeError, match="_format_numeric_value expected format_code"):
        _format_numeric_value(1.2, 1)


@pytest.mark.parametrize(
    ("value", "format_codes", "expected"),
    [
        (5, None, "5"),
        (3.2, None, "3.2"),
        (np.int64(7), None, "7"),
        (np.float64(1.5), None, "1.5"),
        (np.array(7), None, "7"),
        (np.array([[0, 1], [2, 3]]), None, "[0 1; 2 3]"),
        (np.array([[1.5, 2.0]]), None, "[1.5 2.0]"),
        (np.array([[1], [2]]), None, "[1; 2]"),
        (np.nan, None, "NaN"),
        (np.array(np.nan), None, "NaN"),
        (np.inf, None, "Inf"),
        (-np.inf, None, "-Inf"),
        (np.array([[1.0, np.nan], [np.inf, -np.inf]]), None, "[1.0 NaN; Inf -Inf]"),
        (3.14159, ".2f", "3.14"),
        (np.array(3.14159), ".3f", "3.142"),
        (np.array([[1.234, 5.678], [9.876, 1.234]]), ".1f", "[1.2 5.7; 9.9 1.2]"),
        (np.nan, ".2f", "NaN"),
        (
            np.array([[1.234, 5.678], [9.876, 1.234]]),
            [".1f", ".0f"],
            "[1.2 6; 9.9 1]",
        ),
        (
            np.array([[1.234, np.nan], [np.inf, 1.234]]),
            [".1f", ".0f"],
            "[1.2 NaN; Inf 1]",
        ),
    ],
)
def test_convert_numeric_array_to_matlab_supported_shapes(value, format_codes, expected):
    assert convert_numeric_array_to_matlab(value, format_codes=format_codes) == expected


@pytest.mark.parametrize(
    "value",
    [
        "1",
        [1, 2],
        True,
        np.bool_(True),
        1 + 2j,
        np.complex64(1 + 2j),
        np.array(["1"]),
        np.array([object()], dtype=object),
        np.array([True, False]),
        np.array([1 + 2j]),
    ],
)
def test_convert_numeric_array_to_matlab_rejects_non_numeric_inputs(value):
    with pytest.raises(TypeError, match="convert_numeric_array_to_matlab expected array"):
        convert_numeric_array_to_matlab(value)


@pytest.mark.parametrize("value", [np.array([1, 2]), np.ones((1, 1, 1))])
def test_convert_numeric_array_to_matlab_rejects_unsupported_array_dimensions(value):
    with pytest.raises(ValueError, match="scalar or 2D"):
        convert_numeric_array_to_matlab(value)


@pytest.mark.parametrize("format_codes", [1, object(), {".1f"}])
def test_convert_numeric_array_to_matlab_rejects_invalid_format_codes_type(format_codes):
    with pytest.raises(TypeError, match="format_codes"):
        convert_numeric_array_to_matlab(np.array([[1.0, 2.0]]), format_codes=format_codes)


def test_convert_numeric_array_to_matlab_rejects_invalid_format_code_items():
    with pytest.raises(TypeError, match="item 1 is int"):
        convert_numeric_array_to_matlab(
            np.array([[1.0, 2.0]]),
            format_codes=[".1f", 2],
        )


def test_convert_numeric_array_to_matlab_rejects_wrong_number_of_column_formats():
    with pytest.raises(ValueError, match="Expected 2 format codes, got 1"):
        convert_numeric_array_to_matlab(np.array([[1.0, 2.0]]), format_codes=[".1f"])


@pytest.mark.parametrize(
    ("value", "double_brackets", "expected"),
    [
        (["a", "b"], False, "{'a', 'b'}"),
        ([], False, "{}"),
        (["Pen_2"], True, "{{'Pen_2'}}"),
        (("O'Brien", "Pen_2"), False, "{'O''Brien', 'Pen_2'}"),
    ],
)
def test_convert_list_of_strings_to_matlab(value, double_brackets, expected):
    assert convert_list_of_strings_to_matlab(value, double_brackets=double_brackets) == expected


@pytest.mark.parametrize("value", ["a", {"a": 1}, 1, None])
def test_convert_list_of_strings_to_matlab_rejects_non_collections(value):
    with pytest.raises(TypeError, match="convert_list_of_strings_to_matlab expected list_data"):
        convert_list_of_strings_to_matlab(value)


@pytest.mark.parametrize("value", [[1], ["a", 1], ("a", None)])
def test_convert_list_of_strings_to_matlab_rejects_non_string_items(value):
    with pytest.raises(TypeError, match="expected every item in list_data"):
        convert_list_of_strings_to_matlab(value)


def test_convert_list_of_strings_to_matlab_rejects_invalid_double_brackets_type():
    with pytest.raises(TypeError, match="double_brackets"):
        convert_list_of_strings_to_matlab(["a"], double_brackets=1)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("O'Brien", "'O''Brien'"),
        (["a", "b"], "{'a', 'b'}"),
        (("O'Brien", "b"), "{'O''Brien', 'b'}"),
    ],
)
def test_convert_string_or_collection_to_matlab(value, expected):
    assert convert_string_or_collection_to_matlab(value) == expected


@pytest.mark.parametrize("value", [1, None, {"a": "b"}])
def test_convert_string_or_collection_to_matlab_rejects_invalid_values(value):
    with pytest.raises(TypeError, match="convert_string_or_collection_to_matlab expected value"):
        convert_string_or_collection_to_matlab(value)


def test_convert_string_or_collection_to_matlab_rejects_non_string_collection_items():
    with pytest.raises(TypeError, match="expected every item in list_data"):
        convert_string_or_collection_to_matlab([1])


@pytest.mark.parametrize(
    ("value", "is_string_data", "expected"),
    [
        ({}, False, "struct()"),
        ({"PT1": 507, "PT2": 545}, False, "struct('PT1', 507, 'PT2', 545)"),
        ({"PT1": np.nan, "PT2": np.inf, "PT3": -np.inf}, False, "struct('PT1', NaN, 'PT2', Inf, 'PT3', -Inf)"),
        ({"enabled": True, "disabled": np.bool_(False)}, False, "struct('enabled', 1, 'disabled', 0)"),
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
        (
            {"species": "O'Brien"},
            True,
            "struct('species', 'O''Brien')",
        ),
    ],
)
def test_convert_dict_to_matlab(value, is_string_data, expected):
    assert convert_dict_to_matlab(value, is_string_data=is_string_data) == expected


@pytest.mark.parametrize("value", [[], None, "not a dict"])
def test_convert_dict_to_matlab_rejects_non_dict_values(value):
    with pytest.raises(TypeError, match="convert_dict_to_matlab expected dict_data"):
        convert_dict_to_matlab(value)


def test_convert_dict_to_matlab_rejects_invalid_is_string_data_type():
    with pytest.raises(TypeError, match="is_string_data"):
        convert_dict_to_matlab({"value": "x"}, is_string_data=1)


@pytest.mark.parametrize("value", [{1: "x"}, {None: "x"}])
def test_convert_dict_to_matlab_rejects_non_string_keys(value):
    with pytest.raises(TypeError, match="every key in dict_data"):
        convert_dict_to_matlab(value)


@pytest.mark.parametrize(
    "value",
    [
        {"value": []},
        {"value": {}},
        {"value": np.array(1)},
        {"value": 1 + 2j},
    ],
)
def test_convert_dict_to_matlab_rejects_invalid_values(value):
    with pytest.raises(TypeError, match="every value in dict_data"):
        convert_dict_to_matlab(value)


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
