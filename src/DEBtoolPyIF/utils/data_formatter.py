import os
import re


def check_files_exist_in_folder(folder_name, files):
    if not isinstance(files, (list, tuple)):
        files = (files,)
    for f in files:
        if not os.path.exists(f"{folder_name}/{f}"):
            return False, f
    return True, "All good!"


def format_string_list_data(list_data: list, double_brackets: bool = False):
    formatted_list = '{' + list_data.__repr__()[1:-1] + '}'
    if double_brackets:
        formatted_list = '{' + formatted_list + '}'
    return formatted_list


def format_dict_data(dict_data: dict, is_string_data=False):
    # Return empty struct if dict is empty
    if not dict_data:
        return 'struct()'
    formatted = 'struct('
    for k, v in dict_data.items():
        if is_string_data:
            v = "'" + str(v) + "'"
        formatted += f"'{k}', {v}, "
    formatted = formatted[:-2] + ')'
    return formatted


def format_tier_variable(var_name, formatted_data, label, units='-', bibkey='', comment='', pars_init_access=False):
    s = f"data.{var_name} = 10; " \
        f"units.{var_name} = '-'; " \
        f"label.{var_name} = 'Dummy variable'; "
    if comment:
        s += f"comment.{var_name} = '{comment}'; "
    if bibkey:
        s += f"bibkey.{var_name} = '{bibkey}';"
    s += f"\ntiers.{var_name} = {formatted_data}; " \
         f"units.tiers.{var_name} = '{units}'; " \
         f"label.tiers.{var_name} = '{label}'; \n"
    if pars_init_access:
        s += f"metaData.{var_name} = tiers.{var_name}; % Save in metaData to use in pars_init.m"
    return s


def format_meta_data(var_name, formatted_data):
    return f"metaData.{var_name} = {formatted_data}; \n"


def is_valid_matlab_field_name(fieldname: str) -> bool:
    """
    Checks if a string is a valid MATLAB struct field name.
    :param fieldname: The string to check.
    :return: True, if field name is a valid MATLAB struct field name.
    """
    if not fieldname:
        return False
    # First character must be a letter, rest can be letters, digits, or underscores
    return bool(re.match(r'^[A-Za-z][A-Za-z0-9_]*$', fieldname))


def sanitize_matlab_field_name(fieldname: str) -> str:
    """
    Converts a string into a valid MATLAB struct field name. Replaces invalid characters with underscores. If the first
    character is not a letter, prepends 'x'.
    :param fieldname: The MATLAB struct field name to sanitize.
    :return: The MATLAB struct field name
    """
    if not fieldname:
        return "x"

    # Replace invalid chars with underscores
    fieldname = re.sub(r'[^A-Za-z0-9_]', '_', fieldname)

    # Ensure first char is a letter
    if not re.match(r'^[A-Za-z]', fieldname):
        fieldname = 'x' + fieldname

    return fieldname
