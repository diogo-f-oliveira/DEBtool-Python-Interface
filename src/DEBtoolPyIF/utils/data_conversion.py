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
