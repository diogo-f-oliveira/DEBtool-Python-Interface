import pandas as pd

from ..utils.mydata_code_generation import is_valid_matlab_field_name, generate_data_code, generate_aux_data_code
from ..utils.data_conversion import convert_numeric_array_to_matlab, convert_string_to_matlab, \
    convert_list_of_strings_to_matlab
from ..utils.entity_list import normalize_entity_list


class DataSourceBase:
    TYPE = ''
    LABELS = ''
    AUX_DATA_LABELS = ''

    def __init__(self, csv_filename: str, id_col: str, dep_var_col: str, dep_var_unit: str, name: str = None,
                 indep_var_col: str = None, indep_var_unit: str = '', aux_datasource=None,
                 prefix: str = '', title: str = '', bibkey: str = '', comment: str = '', id_name: str = '',
                 ):
        self.csv_filename = csv_filename
        self.id_col = id_col
        # Set dependent data
        self.dep_var_col = dep_var_col
        self.dep_var_unit = dep_var_unit
        # Load dataframe
        self.df = pd.read_csv(self.csv_filename)
        # Check if dependent variable column exists in df
        if dep_var_col not in self.df.columns:
            raise Exception(f'Column {dep_var_col} not found in {self.csv_filename}.')

        # Drop rows where data is missing
        # TODO: Think about cases where this is not good to do. DEBtool can handle nan values for example for
        #  multivariate datasets, so maybe we should not do this.
        columns_to_check_for_na = [id_col, dep_var_col]
        if indep_var_col is not None:
            columns_to_check_for_na += [indep_var_col]
        self.df.dropna(subset=columns_to_check_for_na, how='any', inplace=True)

        # Set ids as string and add prefix to id column
        self.df[self.id_col] = self.df[self.id_col].astype(str)
        self.prefix = prefix
        if self.prefix:
            self.df[self.id_col] = f"{self.prefix}_" + self.df[self.id_col]
        # TODO: Check if ids are valid

        # Set independent variable
        self.indep_var_col = indep_var_col
        self.indep_var_unit = indep_var_unit

        # Set aux data variable
        self.aux_datasource = aux_datasource

        # Set the name and info of the datasource
        if name is None:
            name = csv_filename.split('/')[-1][:-4] + '_' + self.TYPE
        self.name = name

        self.bibkey = bibkey
        self.comment = comment
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

    def generate_dataset_code(self, id_, data, converted_aux_data: str = None, auxdata_struct_name=''):
        converted_data = convert_numeric_array_to_matlab(data)
        var_name = f"{self.TYPE}_{id_}"
        title = '' if self.is_zero_variate else f"{self.title}, {self.id_name} {id_}"
        dataset_code = generate_data_code(var_name=var_name, converted_data=converted_data, units=self.units,
                                          label=self.labels, bibkey=self.bibkey, comment=self.comment,
                                          title=title)
        if converted_aux_data is not None:
            if not auxdata_struct_name:
                raise Exception('Struct name is required when auxiliary data is provided.')
            dataset_code += generate_aux_data_code(var_name=var_name, converted_data=converted_aux_data,
                                                   struct_name=auxdata_struct_name, label=self.aux_data_labels,
                                                   units=self.aux_data_units)
        return dataset_code

    @staticmethod
    def generate_info_matlab_code(info):
        if isinstance(info, str):
            return convert_string_to_matlab(info)
        elif isinstance(info, (tuple, list)):
            return convert_list_of_strings_to_matlab(info)
        else:
            raise TypeError(f'Unexpected type {type(info)}. Units and Labels should be either a string or a tuple or '
                            f'list of strings.')

    @property
    def units(self):
        if self.is_zero_variate:
            units = self.dep_var_unit
        else:
            units = (self.indep_var_unit, self.dep_var_unit)
        return self.generate_info_matlab_code(units)

    @property
    def is_zero_variate(self):
        return self.indep_var_col is None

    @property
    def labels(self):
        return self.generate_info_matlab_code(self.LABELS)

    @property
    def has_aux_data(self):
        return self.aux_datasource is not None

    @property
    def aux_data_units(self):
        return self.generate_info_matlab_code(self.aux_datasource.dep_var_unit)

    @property
    def aux_data_labels(self):
        return self.generate_info_matlab_code(self.AUX_DATA_LABELS)


class EntityDataSourceBase(DataSourceBase):
    def __init__(self, csv_filename: str, id_col: str, dep_var_col: str, dep_var_unit: str, name: str = None,
                 indep_var_col: str = None, indep_var_unit: str = '', aux_datasource: DataSourceBase = None,
                 prefix: str = '', bibkey: str = '', comment: str = '', title: str = '', id_name: str = '',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=dep_var_col, dep_var_unit=dep_var_unit,
                         indep_var_col=indep_var_col, indep_var_unit=indep_var_unit,
                         aux_datasource=aux_datasource,
                         prefix=prefix, bibkey=bibkey, comment=comment, title=title, id_name=id_name,
                         )

        # Find the ids of all individuals
        # TODO: use sanitize function instead of just replacing spaces?
        self.entities = {str(ci).replace(' ', '_') for ci in self.df[id_col].unique()}

    def get_entity_data(self, entity_id):
        if entity_id not in self.entities:
            raise Exception(f'Invalid entity ID. Entity {entity_id} not found in the dataset.')
        return self.groupbys.get_group(entity_id)


class ZeroVariateEntityDataSource(EntityDataSourceBase):
    def __init__(self, csv_filename: str, id_col: str, dep_var_col: str, dep_var_unit: str, name: str = None,
                 aux_datasource: DataSourceBase = None,
                 prefix: str = '', bibkey: str = '', comment: str = '', id_name: str = '',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=dep_var_col, dep_var_unit=dep_var_unit,
                         aux_datasource=aux_datasource,
                         prefix=prefix, bibkey=bibkey, comment=comment, id_name=id_name,
                         )
        # Set id_col as the index of the dataframe
        self.df.set_index(id_col, inplace=True)

    def get_entity_data(self, entity_id):
        if entity_id not in self.entities:
            raise Exception(f'Invalid entity ID. Entity {entity_id} not found in the dataset.')
        return self.df.loc[entity_id, self.dep_var_col]


class GroupDataSourceBase(DataSourceBase):

    def __init__(self, csv_filename: str, id_col: str, dep_var_col: str, dep_var_unit: str, name: str = None,
                 indep_var_col: str = None, indep_var_unit: str = '', aux_datasource: DataSourceBase = None,
                 prefix: str = '', bibkey: str = '', comment: str = '', title: str = '', id_name: str = '',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=dep_var_col, dep_var_unit=dep_var_unit,
                         indep_var_col=indep_var_col, indep_var_unit=indep_var_unit,
                         aux_datasource=aux_datasource,
                         prefix=prefix, bibkey=bibkey, comment=comment, title=title, id_name=id_name,
                         )

        # Find the ids of all groups
        self.groups = {str(ci).replace(' ', '_') for ci in self.df[self.id_col].unique()}
        self.entity_vs_group_df = pd.DataFrame(columns=sorted(self.groups))

    def create_entity_vs_group_df(self, entity_data_source: EntityDataSourceBase):
        for entity_id in list(entity_data_source.entities):
            group_id = entity_data_source.get_entity_data(entity_id)[self.id_col].iloc[0]
            self.entity_vs_group_df.loc[entity_id, group_id] = True

    def get_groups_in_entity_list(self, entity_list):
        # Only returns groups of individuals that exist in the data
        entity_list = normalize_entity_list(entity_list, allow_all=False)
        entity_list = [entity_id for entity_id in entity_list if entity_id in self.entity_vs_group_df.index]
        return sorted(self.entity_vs_group_df.loc[entity_list].dropna(axis=1, how='all').columns)

    def get_entity_list_of_group(self, group_id):
        return sorted(self.entity_vs_group_df[group_id].dropna().index)

    def get_group_data(self, group_id):
        if group_id not in self.groups:
            raise Exception(f'Invalid Group ID. Group {group_id} not found in the dataset.')
        return self.groupbys.get_group(group_id)


class ZeroVariateGroupDataSourceBase(GroupDataSourceBase):

    def __init__(self, csv_filename: str, id_col: str, dep_var_col: str, dep_var_unit: str, name: str = None,
                 aux_datasource: str = None,
                 prefix: str = '', bibkey: str = '', comment: str = '', id_name: str = '',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=dep_var_col, dep_var_unit=dep_var_unit,
                         aux_datasource=aux_datasource,
                         prefix=prefix, bibkey=bibkey, comment=comment, id_name=id_name,
                         )
