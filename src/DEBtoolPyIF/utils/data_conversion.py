import numpy as np


def convert_string_to_matlab(string: str) -> str:
    return string.__repr__()


def convert_numeric_array_to_matlab(array: [int, float, np.array]):
    if np.size(array) == 1:
        if isinstance(array, np.ndarray):
            return array.item()
        else:
            return array
    else:
        rows = []
        for row in array:  # flatten higher dims into 2D
            row_str = " ".join(str(x) for x in row)
            rows.append(row_str)
        matlab_code = "; ".join(rows)
        return f"[{matlab_code}]"


def convert_list_of_strings_to_matlab(list_data: list, double_brackets: bool = False):
    matlab_code = '{' + list_data.__repr__()[1:-1] + '}'
    if double_brackets:
        matlab_code = '{' + matlab_code + '}'
    return matlab_code


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
