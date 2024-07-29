import pandas as pd

from src.DEBtoolPyIF.data_sources.base import IndDataSourceBase, GroupDataSourceBase


class DataCollection:
    def __init__(self, data_sources: list):
        self._individuals = set()
        self._groups = set()
        self.data_sources = {}
        self.group_data_sources = {}
        self.ind_data_sources = {}
        self.data_source_of_ind_df = pd.DataFrame()
        self.data_source_of_group_df = pd.DataFrame()
        self.data_type_of_data_source_df = pd.DataFrame()
        self.group_of_ind_df = pd.DataFrame()
        for ds in data_sources:
            self.add_data_source(ds)

    def add_data_source(self, data_source):
        self.data_sources[data_source.name] = data_source
        self.data_type_of_data_source_df.loc[data_source.name, data_source.TYPE] = True
        if isinstance(data_source, IndDataSourceBase):
            self.ind_data_sources[data_source.name] = data_source
            # Update data_source_of_ind_df with new individuals
            ds_group_of_ind = pd.DataFrame(index=list(data_source.individuals))
            ds_of_ind_df = pd.DataFrame(index=list(data_source.individuals), columns=[data_source.name])
            ds_of_ind_df[data_source.name] = True
            self.data_source_of_ind_df = pd.concat([self.data_source_of_ind_df, ds_of_ind_df]).groupby(level=0).max()
        elif isinstance(data_source, GroupDataSourceBase):
            self.group_data_sources[data_source.name] = data_source
            # Update data_source_of_group_df with new groups
            ds_group_of_ind = data_source.group_of_ind_df
            ds_of_group_df = pd.DataFrame(index=list(data_source.groups), columns=[data_source.name])
            ds_of_group_df[data_source.name] = True
            self.data_source_of_group_df = pd.concat([self.data_source_of_group_df,
                                                      ds_of_group_df]).groupby(level=0).max()
        else:
            raise Exception('Data sources must based on IndDataSourceBase or GroupDataSourceBase class')

        # Combine group_of_ind dataframes
        self.group_of_ind_df = pd.concat([self.group_of_ind_df, ds_group_of_ind]).groupby(level=0).max()
        # Update sets of inds and groups
        self._individuals = set(self.group_of_ind_df.index)
        self._groups = set(self.group_of_ind_df.columns)

    def get_mydata_code(self, ind_list='all'):
        return [ds.generate_code(ind_list=ind_list) for ds in self.data_sources.values()]

    def get_ind_data_code(self, ind_list='all'):
        return [ds.generate_code(ind_list=ind_list) for ds in self.ind_data_sources.values()]

    def get_group_data_code(self, ind_list='all'):
        return [ds.generate_code(ind_list=ind_list) for ds in self.group_data_sources.values()]

    @property
    def data_types(self):
        return sorted(self.data_type_of_data_source_df.columns)

    @property
    def ind_data_types(self):
        return sorted(set([ds.TYPE for ds in self.ind_data_sources.values()]))

    @property
    def group_data_types(self):
        return sorted(set([ds.TYPE for ds in self.group_data_sources.values()]))

    @property
    def individuals(self):
        return sorted(self._individuals)

    @property
    def groups(self):
        return sorted(self._groups)

    def get_ind_list_of_group(self, group_id):
        return sorted(self.group_of_ind_df[group_id].dropna().index)

    def get_groups_of_ind_list(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = self.individuals

        groups_of_ind = {ind_id: [] for ind_id in ind_list if ind_id in self._individuals}
        for ind_id in groups_of_ind.keys():
            groups_of_ind[ind_id].extend(self.group_of_ind_df.loc[ind_id].dropna().index)
        return groups_of_ind

    def get_group_list_from_ind_list(self, ind_list='all'):
        if ind_list == 'all':
            return self.groups
        return sorted(self.group_of_ind_df.loc[ind_list].dropna(axis=1, how='all').columns)
        # groups_of_ind = self.get_groups_of_ind_list(ind_list)
        # return sorted({g for g_list in groups_of_ind.values() for g in g_list})

    def get_data_source_of_ind(self, ind_id, data_type):
        data_sources_of_data_type = self.data_type_of_data_source_df[data_type].dropna().index
        data_sources_with_data_of_ind = self.data_source_of_ind_df.loc[ind_id].dropna().index
        return list(data_sources_of_data_type.intersection(data_sources_with_data_of_ind))

    def get_ind_data(self, ind_id, data_type):
        ind_data = []
        for ds_name in self.get_data_source_of_ind(ind_id, data_type):
            ind_data.append(self.ind_data_sources[ds_name].get_ind_data(ind_id))
        if len(ind_data):
            return pd.concat(ind_data)
        else:
            return None

    def get_data_source_of_group(self, group_id, data_type):
        data_sources_of_data_type = self.data_type_of_data_source_df[data_type].dropna().index
        data_sources_with_data_of_group = self.data_source_of_group_df.loc[group_id].dropna().index
        return list(data_sources_of_data_type.intersection(data_sources_with_data_of_group))

    def get_group_data(self, group_id, data_type):
        group_data = []
        for ds_name in self.get_data_source_of_group(group_id, data_type):
            group_data.append(self.group_data_sources[ds_name].get_group_data(group_id))
        if len(group_data):
            return pd.concat(group_data)
        else:
            return None
