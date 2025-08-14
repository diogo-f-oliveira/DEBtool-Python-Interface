import pandas as pd


class DataSourceBase:
    TYPE = ''
    LABELS = ''
    AUX_DATA_LABELS = ''

    def __init__(self, csv_filename, id_col, name=None,
                 prefix='', bibkey='', comment='',
                 ind_var_unit='', dep_var_unit='', aux_var_unit='',
                 ):
        self.csv_filename = csv_filename
        self.id_col = id_col
        # Load dataframe
        self.df = pd.read_csv(self.csv_filename)

        # Load dataframe
        self.df = pd.read_csv(self.csv_filename)
        # Set ids as string and add prefix
        self.df[self.id_col] = self.df[self.id_col].astype(str)
        self.prefix = prefix
        if self.prefix:
            self.df[self.id_col] = f"{self.prefix}_" + self.df[self.id_col]

        # Set the name and info of the datasource
        if name is None:
            name = csv_filename.split('/')[-1][:-4] + '_' + self.TYPE
        self.name = name
        self.bibkey = bibkey
        self.comment = comment
        self._units = (ind_var_unit, dep_var_unit)
        self._aux_data_units = aux_var_unit

        # Save groupby structure for faster processing
        self.groupbys = self.df.groupby(self.id_col)

    def generate_code(self):
        return

    def format_info(self, units):
        if isinstance(units, str):
            formatted_units = f"'{units}'"
        elif isinstance(units, (tuple, list)):
            formatted_units = '{'
            for unit in units:
                formatted_units += f"'{unit}', "
            formatted_units = formatted_units[:-2] + "};"
        else:
            raise TypeError(f'Unexpected type {type(units)}. Units and Labels should be either a string or a tuple or '
                            f'list of strings.')
        return formatted_units

    @property
    def units(self):
        return self.format_info(self._units)

    @property
    def labels(self):
        return self.format_info(self.LABELS)

    @property
    def aux_data_units(self):
        return self.format_info(self._aux_data_units)

    @property
    def aux_data_labels(self):
        return self.format_info(self.AUX_DATA_LABELS)


class IndDataSourceBase(DataSourceBase):

    def __init__(self, csv_filename, id_col, name=None,
                 prefix='', bibkey='', comment='',
                 ind_var_unit='', dep_var_unit='', aux_var_unit='',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         prefix=prefix, bibkey=bibkey, comment=comment,
                         ind_var_unit=ind_var_unit, dep_var_unit=dep_var_unit, aux_var_unit=aux_var_unit)

        # Find the ids of all individuals
        self.individuals = {str(ci).replace(' ', '_') for ci in self.df[id_col].unique()}

    def generate_code(self, ind_list='all'):
        return

    def get_ind_data(self, ind_id):
        if ind_id not in self.individuals:
            raise Exception('Invalid ind_id, individual not found in the dataset')
        return self.groupbys.get_group(ind_id)


class GroupDataSourceBase(DataSourceBase):

    def __init__(self, csv_filename, id_col, name=None,
                 prefix='', bibkey='', comment='',
                 ind_var_unit='', dep_var_unit='', aux_var_unit='',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         prefix=prefix, bibkey=bibkey, comment=comment,
                         ind_var_unit=ind_var_unit, dep_var_unit=dep_var_unit, aux_var_unit=aux_var_unit)

        # Find the ids of all groups
        self.groups = {str(ci).replace(' ', '_') for ci in self.df[self.id_col].unique()}
        self.group_of_ind_df = pd.DataFrame(columns=sorted(self.groups))

    def create_group_of_ind_df(self, ind_data_source: IndDataSourceBase):
        for ind_id in list(ind_data_source.individuals):
            group_id = ind_data_source.get_ind_data(ind_id)[self.id_col].iloc[0]
            self.group_of_ind_df.loc[ind_id, group_id] = True

    def get_groups_in_ind_list(self, ind_list):
        # Only returns groups of individuals that exist in the data
        ind_list = [ind_id for ind_id in ind_list if ind_id in self.group_of_ind_df.index]
        return sorted(self.group_of_ind_df.loc[ind_list].dropna(axis=1, how='all').columns)

    def get_ind_list_of_group(self, group_id):
        return sorted(self.group_of_ind_df[group_id].dropna().index)

    def get_group_data(self, group_id):
        if group_id not in self.groups:
            raise Exception('Invalid group_id, group not found in the dataset')
        return self.groupbys.get_group(group_id)

    def generate_code(self, ind_list='all'):
        return
