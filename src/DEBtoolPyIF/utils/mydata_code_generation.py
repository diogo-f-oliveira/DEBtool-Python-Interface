import os
import re


def check_files_exist_in_folder(folder_name, files):
    if not isinstance(files, (list, tuple)):
        files = (files,)
    for f in files:
        if not os.path.exists(f"{folder_name}/{f}"):
            return False, f
    return True, "All good!"


def generate_dataset_code(var_name, formatted_data):
    return


def generate_aux_data_code(var_name, formatted_data, struct_name, label, units):
    """
    Generates the code for an auxiliary dataset
    :param var_name: the name of the dataset
    :param formatted_data: the data already formatted in MATLAB syntax
    :param struct_name: the name of the struct where to save the auxiliary data
    :param label: the label of the auxiliary data
    :param units: the units of the auxiliary data
    :return: the MATLAB code for the auxiliary data
    """
    formatted_aux_data = f"\n{struct_name}.{var_name} = {formatted_data}; " \
                        f"units.{struct_name}.{var_name} = '{units}'; " \
                        f"label.{struct_name}.{var_name} = '{label}'; \n"
    return formatted_aux_data


def generate_meta_data_code(var_name, formatted_data):
    return f"metaData.{var_name} = {formatted_data}; \n"


def generate_tier_variable_code(var_name, formatted_data, label, units='-', bibkey='', comment='', pars_init_access=False):
    s = f"data.{var_name} = 10; " \
        f"units.{var_name} = '-'; " \
        f"label.{var_name} = 'Tier structure variable'; "
    if comment:
        s += f"comment.{var_name} = '{comment}'; "
    if bibkey:
        s += f"bibkey.{var_name} = '{bibkey}';"
    s += generate_aux_data_code(var_name, formatted_data, struct_name='tiers', label=label, units=units)
    if pars_init_access:
        s += generate_meta_data_code(var_name, formatted_data=f"tiers.{var_name}")
    return s


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
