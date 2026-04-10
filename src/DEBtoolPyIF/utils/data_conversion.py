from collections.abc import Sequence

import numpy as np


def convert_string_to_matlab(string: str) -> str:
    return f"'{string}'"


def _format_numeric_value(value, format_code: str | None = None):
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
    array: int | float | np.ndarray,
    format_codes: str | Sequence[str] | None = None,
) -> str:
    if np.size(array) == 1: # Covers case for int and float
        if isinstance(array, np.ndarray):
            return _format_numeric_value(array.item(), format_codes)
        return _format_numeric_value(array, format_codes)
    
    if isinstance(format_codes, str) or format_codes is None:
        column_format_codes = format_codes
    else:
        column_format_codes = list(format_codes)
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


def convert_list_of_strings_to_matlab(list_data: list, double_brackets: bool = False):
    matlab_code = '{' + list_data.__repr__()[1:-1] + '}'
    if double_brackets:
        matlab_code = '{' + matlab_code + '}'
    return matlab_code


def convert_string_or_collection_to_matlab(value: str | list[str] | tuple[str, ...]) -> str:
    if isinstance(value, (list, tuple)):
        return convert_list_of_strings_to_matlab(list(value))
    return convert_string_to_matlab(value)


def convert_dict_to_matlab(dict_data: dict, is_string_data=False):
    # Return empty struct if dict is empty
    if not dict_data:
        return 'struct()'
    matlab_code = 'struct('
    for k, v in dict_data.items():
        if is_string_data:
            v = "'" + str(v) + "'"
        matlab_code += f"'{k}', {v}, "
    matlab_code = matlab_code[:-2] + ')'
    return matlab_code
