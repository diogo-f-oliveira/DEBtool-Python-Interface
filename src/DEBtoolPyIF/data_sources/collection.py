import pandas as pd

from ..data_sources.base import DataSourceBase, EntityDataSourceBase, GroupDataSourceBase


def get_mydata_code(data_source_list: list[DataSourceBase], entity_list='all'):
    data_types = []
    mydata_code = []
    for data_source in data_source_list:
        code = data_source.generate_mydata_code(entity_list=entity_list)
        if code:
            mydata_code.append(code)
            data_types.append(data_source.TYPE)
    return data_types, mydata_code


class DataCollection:
    def __init__(self, tier, data_sources: list[DataSourceBase]):
        self.tier = tier
        self.data_sources = {}
        self.entity_data_sources = {}
        self.group_data_sources = {}
        self._entities = set()
        self._groups = set()
        self.data_source_vs_data_type_df = pd.DataFrame()
        self.entity_vs_data_source_df = pd.DataFrame()
        self.group_vs_data_source_df = pd.DataFrame()
        self.entity_vs_group_df = pd.DataFrame()

        for ds in data_sources:
            self.add_data_source(ds)

    def add_data_source(self, data_source: EntityDataSourceBase | GroupDataSourceBase):
        # Add data source to data of tier
        self.data_sources[data_source.name] = data_source
        self.data_source_vs_data_type_df.loc[data_source.name, data_source.TYPE] = True

        # Add entities if entity data source
        if isinstance(data_source, EntityDataSourceBase):
            self.entity_data_sources[data_source.name] = data_source
            self._entities.update(data_source.entities)
            # Create dummy entity vs group df to update self.entity_vs_group_df
            ds_entity_vs_group_df = pd.DataFrame(index=list(data_source.entities))
            # Update self.entity_vs_data_source_df
            ds_entity_vs_data_source_df = pd.DataFrame(index=list(data_source.entities), columns=[data_source.name])
            ds_entity_vs_data_source_df[data_source.name] = True
            self.entity_vs_data_source_df = pd.concat(
                [self.entity_vs_data_source_df, ds_entity_vs_data_source_df]).groupby(level=0).max()
        elif isinstance(data_source, GroupDataSourceBase):
            self.group_data_sources[data_source.name] = data_source
            self._groups.update(data_source.groups)
            # Update self.entity_vs_group_df
            ds_entity_vs_group_df = data_source.entity_vs_group_df
            # Update self.group_vs_data_source_df
            ds_group_vs_data_source_df = pd.DataFrame(index=list(data_source.groups), columns=[data_source.name])
            ds_group_vs_data_source_df[data_source.name] = True
            self.group_vs_data_source_df = pd.concat(
                [self.group_vs_data_source_df, ds_group_vs_data_source_df]).groupby(level=0).max()
        else:
            raise Exception('Data sources must be based on EntityDataSourceBase or GroupDataSourceBase class')
        # Update self.entity_vs_group_df
        self.entity_vs_group_df = pd.concat([self.entity_vs_group_df, ds_entity_vs_group_df]).groupby(level=0).max()

    def get_entity_mydata_code(self, entity_list='all'):
        return get_mydata_code(list(self.entity_data_sources.values()), entity_list)

    def get_group_mydata_code(self, entity_list='all'):
        return get_mydata_code(list(self.group_data_sources.values()), entity_list)

    @property
    def data_types(self):
        return sorted(self.data_source_vs_data_type_df.columns)

    @property
    def entity_data_types(self):
        return sorted(set([ds.TYPE for ds in self.entity_data_sources.values()]))

    @property
    def group_data_types(self):
        return sorted(set([ds.TYPE for ds in self.group_data_sources.values()]))

    @property
    def entities(self):
        return sorted(self._entities)

    @property
    def groups(self):
        return sorted(self._groups)

    def get_entity_list_of_group(self, group_id):
        return sorted(self.entity_vs_group_df[group_id].dropna().index)

    def get_groups_of_entities(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = self.entities

        groups_of_entity = {entity_id: [] for entity_id in entity_list if entity_id in self._entities}
        for entity_id in groups_of_entity.keys():
            groups_of_entity[entity_id].extend(self.entity_vs_group_df.loc[entity_id].dropna().index)
        return groups_of_entity

    def get_group_list_from_entity_list(self, entity_list='all'):
        if not len(self._groups):
            return []
        if entity_list == 'all':
            return self.groups
        entity_list = list(entity_list)
        return sorted(self.entity_vs_group_df.loc[entity_list].dropna(axis=1, how='all').columns)

    def get_data_source_of_entity(self, entity_id, data_type):
        data_sources_of_data_type = self.data_source_vs_data_type_df[data_type].dropna().index
        data_sources_with_data_of_ind = self.entity_vs_data_source_df.loc[entity_id].dropna().index
        return list(data_sources_of_data_type.intersection(data_sources_with_data_of_ind))

    def get_entity_data(self, entity_id, data_type):
        entity_data = []
        for ds_name in self.get_data_source_of_entity(entity_id, data_type):
            entity_data.append(self.entity_data_sources[ds_name].get_entity_data(entity_id))
        if len(entity_data):
            return pd.concat(entity_data)
        else:
            return None

    def get_data_source_of_group(self, group_id, data_type):
        data_sources_of_data_type = self.data_source_vs_data_type_df[data_type].dropna().index
        data_sources_with_data_of_group = self.group_vs_data_source_df.loc[group_id].dropna().index
        return list(data_sources_of_data_type.intersection(data_sources_with_data_of_group))

    def get_group_data(self, group_id, data_type):
        group_data = []
        for ds_name in self.get_data_source_of_group(group_id, data_type):
            group_data.append(self.group_data_sources[ds_name].get_group_data(group_id))
        if len(group_data):
            return pd.concat(group_data)
        else:
            return None
