import re
from pathlib import Path

from .data_conversion import convert_string_to_matlab


def check_files_exist_in_folder(folder_name, files):
    folder_path = Path(folder_name)
    if not isinstance(files, (list, tuple)):
        files = (files,)
    for f in files:
        if not (folder_path / f).exists():
            return False, f
    return True, "All good!"


def generate_data_code(var_name: str, converted_data: str, units: str, label: str, title=None, comment=None,
                       bibkey=None):
    data_code = f"data.{var_name} = {converted_data};\n" \
                f"units.{var_name} = {units}; " \
                + f"label.{var_name} = {label}; "
    if comment:
        data_code += f"comment.{var_name} = '{comment}'; "
    if title:
        data_code += f"title.{var_name} = '{title}'; "
    if bibkey:
        data_code += f"bibkey.{var_name} = '{bibkey}';"

    return data_code


def generate_aux_data_code(var_name, converted_data, struct_name, label, units):
    """
    Generates the code for an auxiliary dataset
    :param var_name: the name of the dataset
    :param converted_data: the data already formatted in MATLAB syntax
    :param struct_name: the name of the struct where to save the auxiliary data
    :param label: the label of the auxiliary data
    :param units: the units of the auxiliary data
    :return: the MATLAB code for the auxiliary data
    """
    aux_data_code = f"\n{struct_name}.{var_name} = {converted_data};\n" \
                    f"units.{struct_name}.{var_name} = {units}; " \
                    f"label.{struct_name}.{var_name} = {label}; \n"
    return aux_data_code


def generate_meta_data_code(var_name, converted_data):
    return f"metaData.{var_name} = {converted_data}; \n"


def generate_dummy_variable_data_code(var_name, comment='', bibkey=''):
    return generate_data_code(var_name=var_name, converted_data='10',
                              units=convert_string_to_matlab('-'),
                              label=convert_string_to_matlab('Dummy variable'),
                              comment=comment, bibkey=bibkey)


def generate_dummy_variable_code(var_name, struct_name: str, converted_data, converted_label, converted_units,
                                 bibkey='', comment='', pars_init_access=False):
    s = generate_dummy_variable_data_code(var_name=var_name, comment=comment, bibkey=bibkey)

    s += generate_aux_data_code(var_name, converted_data, struct_name=struct_name,
                                label=converted_label, units=converted_units)
    if pars_init_access:
        s += generate_meta_data_code(var_name, converted_data=f"{struct_name}.{var_name}")
    return s


def generate_struct_variable_code(var_name, converted_data, struct_name: str, label, units='-', bibkey='',
                                  comment='', pars_init_access=False):
    return generate_dummy_variable_code(var_name=var_name, converted_data=converted_data,
                                        converted_label=convert_string_to_matlab(label),
                                        converted_units=convert_string_to_matlab(units),
                                        struct_name=struct_name, bibkey=bibkey, comment=comment,
                                        pars_init_access=pars_init_access)


def generate_tier_variable_code(var_name, converted_data, label, units='-', bibkey='', comment='',
                                pars_init_access=False):
    return generate_struct_variable_code(var_name=var_name, converted_data=converted_data,
                                         struct_name='tiers', label=label, units=units,
                                         bibkey=bibkey, comment=comment,
                                         pars_init_access=pars_init_access)


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
