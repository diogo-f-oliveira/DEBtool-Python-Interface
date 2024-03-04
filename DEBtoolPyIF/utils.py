import os


def check_files_exist_in_folder(folder_name, files):
    if not isinstance(files, (list, tuple)):
        files = (files,)
    for f in files:
        if not os.path.exists(f"{folder_name}/{f}"):
            return False, f
    return True, "All good!"

def format_list_data(list_data: list, brackets=False):
    formatted = list_data.__repr__()[1:-1]
    if brackets:
        formatted = '{' + formatted + '}'
    return formatted


def format_dict_data(dict_data: dict):
    formatted = 'struct('
    for k, v in dict_data.items():
        formatted += f"'{k}', {v}, "
    formatted = formatted[:-2] + ')'
    return formatted


def format_aux_data(var_name, formatted_data, label, comment='-', units='-', bibkey='-', pars_init_access=False):
    s = f"data.{var_name} = 10; " \
        f"units.{var_name} = '-'; " \
        f"label.{var_name} = 'Dummy variable'; " \
        f"comment.{var_name} = '{comment}'; " \
        f"bibkey.{var_name} = '{bibkey}'; \n"
    s += f"tiers.{var_name} = {formatted_data}; " \
         f"units.tiers.{var_name} = '{units}'; " \
         f"label.tiers.{var_name} = '{label}'; \n"
    if pars_init_access:
        s += f"metaData.{var_name} = tiers.{var_name}; % Save in metaData to use in pars_init.m"
    return s