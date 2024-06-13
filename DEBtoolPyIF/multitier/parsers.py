import os
import pandas as pd


def parse_tier_pars(tier_folder: str, tier_name=None):
    if tier_name is None:
        tier_name = os.path.basename(tier_folder)
    pars_df = pd.DataFrame()
    for estim_folder in os.listdir(tier_folder):
        if not os.path.isdir(f"{tier_folder}/{estim_folder}"):
            continue
        estim_pars = pd.read_csv(f"{tier_folder}/{estim_folder}/{tier_name}_pars.csv", index_col=0)
        estim_pars['estimation'] = estim_folder
        pars_df = pd.concat([pars_df, estim_pars])
    pars_df.reset_index(inplace=True)
    pars_df.set_index(['estimation', 'tier_sample'], inplace=True)

    return pars_df


def parse_ind_data_errors(tier_folder: str, tier_name=None):
    if tier_name is None:
        tier_name = os.path.basename(tier_folder)
    ind_data_errors_df = pd.DataFrame()
    for estim_folder in os.listdir(tier_folder):
        if not os.path.isdir(f"{tier_folder}/{estim_folder}"):
            continue
        estim_errors = pd.read_csv(f"{tier_folder}/{estim_folder}/{tier_name}_ind_data_errors.csv", index_col=0)
        estim_errors['estimation'] = estim_folder
        ind_data_errors_df = pd.concat([ind_data_errors_df, estim_errors])
    ind_data_errors_df.reset_index(inplace=True)
    ind_data_errors_df.set_index(['estimation', 'ind_id'], inplace=True)

    return ind_data_errors_df


def parse_group_data_errors(tier_folder: str, tier_name=None):
    if tier_name is None:
        tier_name = os.path.basename(tier_folder)
    group_data_errors_df = pd.DataFrame()
    for estim_folder in os.listdir(tier_folder):
        if not os.path.isdir(f"{tier_folder}/{estim_folder}"):
            continue
        estim_errors = pd.read_csv(f"{tier_folder}/{estim_folder}/{tier_name}_group_data_errors.csv", index_col=0)
        estim_errors['estimation'] = estim_folder
        group_data_errors_df = pd.concat([group_data_errors_df, estim_errors])
    group_data_errors_df.reset_index(inplace=True)
    group_data_errors_df.set_index(['estimation', 'group_id'], inplace=True)

    return group_data_errors_df


def parse_tier_errors(tier_folder: str, tier_name=None):
    if tier_name is None:
        tier_name = os.path.basename(tier_folder)
    tier_errors_df = pd.DataFrame()
    for estim_folder in os.listdir(tier_folder):
        if not os.path.isdir(f"{tier_folder}/{estim_folder}"):
            continue
        estim_errors = pd.read_csv(f"{tier_folder}/{estim_folder}/{tier_name}_tier_errors.csv", index_col=0)
        estim_errors['estimation'] = estim_folder
        tier_errors_df = pd.concat([tier_errors_df, estim_errors])
    tier_errors_df.reset_index(inplace=True)
    tier_errors_df.set_index(['estimation', 'tier_sample'], inplace=True)

    return tier_errors_df


if __name__ == '__main__':
    pars_df = parse_tier_pars(
        tier_folder='../../Angus/Methane emissions DEB paper/diet_year/diet_year'
    )
    print(pars_df)
    ind_data_errors_df = parse_ind_data_errors(
        tier_folder='../../Angus/Methane emissions DEB paper/diet_year/diet_year'
    )
    print(ind_data_errors_df)
    group_data_errors_df = parse_group_data_errors(
        tier_folder='../../Angus/Methane emissions DEB paper/diet_year/diet_year'
    )
    print(group_data_errors_df)
    tier_errors_df = parse_tier_errors(
        tier_folder='../../Angus/Methane emissions DEB paper/diet_year/diet_year'
    )
    print(tier_errors_df)
