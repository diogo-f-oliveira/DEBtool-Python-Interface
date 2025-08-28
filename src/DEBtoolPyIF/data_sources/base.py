import pandas as pd

from ..utils.mydata_code_generation import is_valid_matlab_field_name, generate_data_code, generate_aux_data_code
from ..utils.data_conversion import convert_numeric_array_to_matlab


class DataSourceBase:
    TYPE = ''
    LABELS = ''
    AUX_DATA_LABELS = ''

    def __init__(self, csv_filename, id_col, name=None,
                 ind_var_unit='', dep_var_unit='', aux_var_unit='',
                 prefix='', title='', bibkey='', comment='', id_name='',
                 ):
        self.csv_filename = csv_filename
        self.id_col = id_col
        # Load dataframe
        self.df = pd.read_csv(self.csv_filename)

        # Set ids as string and add prefix
        self.df[self.id_col] = self.df[self.id_col].astype(str)
        self.prefix = prefix
        if self.prefix:
            self.df[self.id_col] = f"{self.prefix}_" + self.df[self.id_col]
        # Check if ids are valid

        # Set the name and info of the datasource
        if name is None:
            name = csv_filename.split('/')[-1][:-4] + '_' + self.TYPE
        self.name = name
        self._units = (ind_var_unit, dep_var_unit)
        self._aux_data_units = aux_var_unit
        self.bibkey = bibkey
        self.comment = comment
        if not title:
            title = ' vs '.join(self.LABELS)
        self.title = title
        if id_name is None:
            id_name = self.id_col
        self.id_name = id_name

        # Save groupby structure for faster processing
        self.groupbys = self.df.groupby(self.id_col)

    def check_id_validity(self):
        unique_ids = self.df[self.id_col].unique()
        invalid_ids = [val for val in unique_ids if not is_valid_matlab_field_name(val)]

        if invalid_ids:
            raise Exception(f"DataSource {self.name} has IDs in df.id_col that cannot be used as MATLAB struct field "
                            f"names: {invalid_ids!r}")

    def generate_mydata_code(self, entity_list='all'):
        return

    def generate_dataset_code(self, id_, data, converted_aux_data=None, auxdata_struct_name=''):
        converted_data = convert_numeric_array_to_matlab(data)
        var_name = f"{self.TYPE}_{id_}"
        dataset_code = generate_data_code(var_name=var_name, converted_data=converted_data, units=self.units,
                                          label=self.labels, bibkey=self.bibkey, comment=self.comment,
                                          title=f"{self.title}, {self.id_name} {id_}", )
        if converted_aux_data:
            dataset_code += generate_aux_data_code(var_name=var_name, converted_data=converted_aux_data,
                                                   struct_name=auxdata_struct_name, label=self.aux_data_labels,
                                                   units=self.aux_data_units)
        return dataset_code

    @staticmethod
    def format_info(info):
        if isinstance(info, str):
            return f"'{info}'"
        elif isinstance(info, (tuple, list)):
            formatted_units = '{'
            for unit in info:
                formatted_units += f"'{unit}', "
            return formatted_units[:-2] + '}'
        else:
            raise TypeError(f'Unexpected type {type(info)}. Units and Labels should be either a string or a tuple or '
                            f'list of strings.')

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


class EntityDataSourceBase(DataSourceBase):

    def __init__(self, csv_filename, id_col, name=None,
                 prefix='', bibkey='', comment='', title='', id_name='',
                 ind_var_unit='', dep_var_unit='', aux_var_unit='',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         prefix=prefix, bibkey=bibkey, comment=comment, title=title, id_name=id_name,
                         ind_var_unit=ind_var_unit, dep_var_unit=dep_var_unit, aux_var_unit=aux_var_unit)

        # Find the ids of all individuals
        # TODO: use sanitize function instead of just replacing spaces?
        self.entities = {str(ci).replace(' ', '_') for ci in self.df[id_col].unique()}

    def get_entity_data(self, entity_id):
        if entity_id not in self.entities:
            raise Exception('Invalid ind_id, individual not found in the dataset')
        return self.groupbys.get_group(entity_id)


class GroupDataSourceBase(DataSourceBase):

    def __init__(self, csv_filename, id_col, name=None,
                 prefix='', bibkey='', comment='', title='', id_name='',
                 ind_var_unit='', dep_var_unit='', aux_var_unit='',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         prefix=prefix, bibkey=bibkey, comment=comment, title=title, id_name=id_name,
                         ind_var_unit=ind_var_unit, dep_var_unit=dep_var_unit, aux_var_unit=aux_var_unit)

        # Find the ids of all groups
        self.groups = {str(ci).replace(' ', '_') for ci in self.df[self.id_col].unique()}
        self.entity_vs_group_df = pd.DataFrame(columns=sorted(self.groups))

    def create_entity_vs_group_df(self, entity_data_source: EntityDataSourceBase):
        for entity_id in list(entity_data_source.entities):
            group_id = entity_data_source.get_entity_data(entity_id)[self.id_col].iloc[0]
            self.entity_vs_group_df.loc[entity_id, group_id] = True

    def get_groups_in_entity_list(self, entity_list):
        # Only returns groups of individuals that exist in the data
        entity_list = [entity_id for entity_id in entity_list if entity_id in self.entity_vs_group_df.index]
        return sorted(self.entity_vs_group_df.loc[entity_list].dropna(axis=1, how='all').columns)

    def get_entity_list_of_group(self, group_id):
        return sorted(self.entity_vs_group_df[group_id].dropna().index)

    def get_group_data(self, group_id):
        if group_id not in self.groups:
            raise Exception('Invalid group_id, group not found in the dataset')
        return self.groupbys.get_group(group_id)
