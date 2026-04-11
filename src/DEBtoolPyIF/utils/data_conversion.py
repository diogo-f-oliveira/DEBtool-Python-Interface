from collections.abc import Sequence

import numpy as np


CONVERSION_INPUT_TYPE_MAP = {
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


_NUMERIC_SCALAR_TYPES = (int, float, np.integer, np.floating)
_BOOLEAN_TYPES = (bool, np.bool_)
_STRING_COLLECTION_TYPES = (list, tuple)


def _expected_type_description(function_name: str, parameter_name: str) -> str:
    return CONVERSION_INPUT_TYPE_MAP[function_name][parameter_name]


def _raise_type_error(function_name: str, parameter_name: str, value) -> None:
    expected_type = _expected_type_description(function_name, parameter_name)
    raise TypeError(
        f"{function_name} expected {parameter_name} to be {expected_type}, "
        f"not {type(value).__name__}."
    )


def _validate_parameter_type(
    function_name: str,
    parameter_name: str,
    value,
    expected_types,
) -> None:
    if not isinstance(value, expected_types):
        _raise_type_error(function_name, parameter_name, value)


def _is_real_numeric_scalar(value) -> bool:
    return isinstance(value, _NUMERIC_SCALAR_TYPES) and not isinstance(value, _BOOLEAN_TYPES)


def _validate_real_numeric_scalar(
    function_name: str,
    parameter_name: str,
    value,
) -> None:
    if not _is_real_numeric_scalar(value):
        _raise_type_error(function_name, parameter_name, value)


def _validate_bool_parameter(function_name: str, parameter_name: str, value) -> None:
    _validate_parameter_type(function_name, parameter_name, value, _BOOLEAN_TYPES)


def _validate_string_collection(
    function_name: str,
    parameter_name: str,
    value,
) -> None:
    if not isinstance(value, _STRING_COLLECTION_TYPES):
        _raise_type_error(function_name, parameter_name, value)
    for index, item in enumerate(value):
        if not isinstance(item, str):
            expected_type = _expected_type_description(function_name, parameter_name)
            raise TypeError(
                f"{function_name} expected every item in {parameter_name} to match "
                f"{expected_type}; item {index} is {type(item).__name__}."
            )


def _validate_format_code(format_code: str | None) -> None:
    if format_code is not None and not isinstance(format_code, str):
        _raise_type_error("_format_numeric_value", "format_code", format_code)


def _validate_format_codes(format_codes: str | Sequence[str] | None):
    if format_codes is None or isinstance(format_codes, str):
        return format_codes
    if not isinstance(format_codes, Sequence):
        _raise_type_error("convert_numeric_array_to_matlab", "format_codes", format_codes)

    column_format_codes = list(format_codes)
    for index, format_code in enumerate(column_format_codes):
        if not isinstance(format_code, str):
            expected_type = _expected_type_description(
                "convert_numeric_array_to_matlab",
                "format_codes",
            )
            raise TypeError(
                "convert_numeric_array_to_matlab expected every item in format_codes "
                f"to match {expected_type}; item {index} is {type(format_code).__name__}."
            )
    return column_format_codes


def _validate_numeric_array(array) -> None:
    if isinstance(array, np.ndarray):
        if not (
            np.issubdtype(array.dtype, np.integer)
            or np.issubdtype(array.dtype, np.floating)
        ):
            _raise_type_error("convert_numeric_array_to_matlab", "array", array)
        if array.ndim not in (0, 2):
            raise ValueError(
                "MATLAB numeric arrays must be scalar or 2D, "
                f"not {array.ndim}D."
            )
        return
    _validate_real_numeric_scalar("convert_numeric_array_to_matlab", "array", array)


def _validate_dict_data(dict_data: dict) -> None:
    for key, value in dict_data.items():
        if not isinstance(key, str):
            raise TypeError(
                "convert_dict_to_matlab expected every key in dict_data to be str, "
                f"not {type(key).__name__}."
            )
        if isinstance(value, str):
            continue
        if isinstance(value, _BOOLEAN_TYPES):
            continue
        if _is_real_numeric_scalar(value):
            continue
        expected_type = _expected_type_description("convert_dict_to_matlab", "dict_data")
        raise TypeError(
            "convert_dict_to_matlab expected every value in dict_data to match "
            f"{expected_type}, not {type(value).__name__}."
        )


def convert_string_to_matlab(string: str) -> str:
    _validate_parameter_type("convert_string_to_matlab", "string", string, str)
    return "'" + string.replace("'", "''") + "'"


def _format_numeric_value(value, format_code: str | None = None):
    _validate_real_numeric_scalar("_format_numeric_value", "value", value)
    _validate_format_code(format_code)
    if np.isnan(value):
        return "NaN"
    if np.isposinf(value):
        return "Inf"
    if np.isneginf(value):
        return "-Inf"
    if format_code is None:
        return str(value)
    return format(value, format_code)


def convert_numeric_array_to_matlab(
    array: int | float | np.integer | np.floating | np.ndarray,
    format_codes: str | Sequence[str] | None = None,
) -> str:
    _validate_numeric_array(array)
    column_format_codes = _validate_format_codes(format_codes)

    if np.size(array) == 1:  # Covers case for int and float
        scalar_format_code = column_format_codes
        if isinstance(column_format_codes, list):
            if len(column_format_codes) != 1:
                raise ValueError(
                    f"Expected 1 format code, got {len(column_format_codes)}."
                )
            scalar_format_code = column_format_codes[0]
        if isinstance(array, np.ndarray):
            return _format_numeric_value(array.item(), scalar_format_code)
        return _format_numeric_value(array, scalar_format_code)

    if isinstance(column_format_codes, list):
        n_cols = np.asarray(array).shape[1]
        if len(column_format_codes) != n_cols:
            raise ValueError(
                f"Expected {n_cols} format codes, got {len(column_format_codes)}."
            )

    rows = []
    for row in array:
        if column_format_codes is None:
            row_str = " ".join(str(_format_numeric_value(x)) for x in row)
        elif isinstance(column_format_codes, str):
            row_str = " ".join(
                str(_format_numeric_value(x, column_format_codes)) for x in row
            )
        else:
            row_str = " ".join(
                str(_format_numeric_value(x, fmt))
                for x, fmt in zip(row, column_format_codes)
            )
        rows.append(row_str)
    matlab_code = "; ".join(rows)
    return f"[{matlab_code}]"


def convert_scalar_to_matlab(value: str | bool | int | float | np.number) -> str:
    """Convert a scalar Python value to a MATLAB literal."""

    if isinstance(value, str):
        return convert_string_to_matlab(value)
    if isinstance(value, _BOOLEAN_TYPES):
        return "1" if value else "0"
    if _is_real_numeric_scalar(value):
        return convert_numeric_array_to_matlab(value)
    raise TypeError(
        "convert_scalar_to_matlab expected value to be "
        f"{_expected_type_description('convert_scalar_to_matlab', 'value')}, "
        f"not {type(value).__name__}."
    )


def convert_list_of_strings_to_matlab(
    list_data: list[str] | tuple[str, ...],
    double_brackets: bool = False,
):
    _validate_string_collection(
        "convert_list_of_strings_to_matlab",
        "list_data",
        list_data,
    )
    _validate_bool_parameter(
        "convert_list_of_strings_to_matlab",
        "double_brackets",
        double_brackets,
    )
    matlab_code = "{" + ", ".join(convert_string_to_matlab(item) for item in list_data) + "}"
    if double_brackets:
        matlab_code = "{" + matlab_code + "}"
    return matlab_code


def convert_string_or_collection_to_matlab(value: str | list[str] | tuple[str, ...]) -> str:
    if isinstance(value, _STRING_COLLECTION_TYPES):
        return convert_list_of_strings_to_matlab(value)
    if isinstance(value, str):
        return convert_string_to_matlab(value)
    _raise_type_error("convert_string_or_collection_to_matlab", "value", value)


def convert_dict_to_matlab(dict_data: dict, is_string_data=False):
    _validate_parameter_type("convert_dict_to_matlab", "dict_data", dict_data, dict)
    _validate_bool_parameter("convert_dict_to_matlab", "is_string_data", is_string_data)
    _validate_dict_data(dict_data)

    # Return empty struct if dict is empty
    if not dict_data:
        return 'struct()'
    matlab_code = 'struct('
    for k, v in dict_data.items():
        if is_string_data:
            v = convert_string_to_matlab(str(v))
        elif not isinstance(v, str):
            v = convert_scalar_to_matlab(v)
        matlab_code += f"{convert_string_to_matlab(k)}, {v}, "
    matlab_code = matlab_code[:-2] + ')'
    return matlab_code
