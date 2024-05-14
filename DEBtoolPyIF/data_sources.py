import pandas as pd
from .utils import format_dict_data


class IndDataSourceBase:
    TYPE = ''

    def __init__(self, csv_filename, id_col, name=None, prefix=''):
        # TODO: Add bibkey and comment to base class
        self.csv_filename = csv_filename
        self.id_col = id_col

        # Load dataframe
        self.df = pd.read_csv(self.csv_filename)
        # Set ids as string and add prefix
        self.df[self.id_col] = self.df[self.id_col].astype(str)
        self.prefix = prefix
        if self.prefix:
            self.df[self.id_col] = f"{self.prefix}_" + self.df[self.id_col]
        # Set the name of the datasource
        if name is None:
            name = csv_filename.split('/')[-1][:-4] + '_' + self.TYPE
        self.name = name
        # Find the ids of all individuals
        self.individuals = {str(ci).replace(' ', '_') for ci in self.df[id_col].unique()}
        # Save groupby structure for faster processing
        self.groupbys = self.df.groupby(self.id_col)

    def generate_code(self, ind_list='all'):
        return

    def get_ind_data(self, ind_id):
        if ind_id not in self.individuals:
            raise Exception('Invalid ind_id, individual not found in the dataset')
        return self.groupbys.get_group(ind_id)


class GroupDataSourceBase:
    TYPE = ''

    def __init__(self, csv_filename, group_col, name=None, prefix=''):
        # TODO: Add bibkey and comment to base class
        self.csv_filename = csv_filename
        self.group_col = group_col

        # Load dataframe
        self.df = pd.read_csv(self.csv_filename)
        # Set ids as string and add prefix
        self.df[self.group_col] = self.df[self.group_col].astype(str)
        self.prefix = prefix
        if self.prefix:
            self.df[self.group_col] = f"{self.prefix}_" + self.df[self.group_col]
        # Find the ids of all groups
        self.groups = {str(ci).replace(' ', '_') for ci in self.df[self.group_col].unique()}
        self.group_of_ind_df = pd.DataFrame(columns=sorted(self.groups))

        # Set the name of the datasource
        if name is None:
            name = csv_filename.split('/')[-1][:-4]
        self.name = name
        # Save groupby structure for faster processing
        self.groupbys = self.df.groupby(self.group_col)

    def create_group_of_ind_df(self, ind_data_source: IndDataSourceBase):
        for ind_id in list(ind_data_source.individuals):
            group_id = ind_data_source.get_ind_data(ind_id)[self.group_col].iloc[0]
            self.group_of_ind_df.loc[ind_id, group_id] = True

    def get_groups_in_ind_list(self, ind_list):
        # Only returns groups of individuals that exist in the data
        ind_list = [ind_id for ind_id in ind_list if ind_id in self.group_of_ind_df.index]
        return sorted(self.group_of_ind_df.loc[ind_list].dropna(axis=1, how='all').columns)
        # return sorted({self.group_of_ind[ind_id] for ind_id in ind_list if ind_id in self.group_of_ind})

    def get_ind_list_of_group(self, group_id):
        return sorted(self.group_of_ind_df[group_id].dropna().index)

    def get_group_data(self, group_id):
        if group_id not in self.groups:
            raise Exception('Invalid group_id, group not found in the dataset')
        return self.groupbys.get_group(group_id)

    def generate_code(self, ind_list='all'):
        return


class DataCollection:
    # TODO: Method to fetch a datasource
    # TODO: Redo based on list
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


class TimeWeightDataSource(IndDataSourceBase):
    TYPE = "tW"
    UNITS = "{'d', 'kg'}"
    LABELS = "{'Time since start', 'Wet weight'}"
    AUX_DATA_UNITS = "'kg'"
    AUX_DATA_LABELS = "'Initial weight'"

    def __init__(self, csv_filename, id_col, weight_col, date_col,
                 name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name, prefix=prefix)
        self.weight_col = weight_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.bibkey = bibkey
        self.comment = comment

    def get_data(self, ind_id):
        ind_data = self.get_ind_data(ind_id).sort_values(by=self.date_col)
        initial_weight = ind_data.iloc[0][self.weight_col]
        initial_date = ind_data.iloc[0][self.date_col]
        return ind_data, initial_date, initial_weight

    def generate_code(self, ind_list='all'):
        # TODO: Check if this is needed
        if ind_list == 'all':
            ind_list = list(self.individuals)

        my_data_code = f'%% Time vs Weight data \n\n'
        for ind_id in ind_list:
            if ind_id not in self.individuals:
                continue
            ind_data, initial_date, initial_weight = self.get_data(ind_id)

            tw_data = f'data.{self.TYPE}_{ind_id} = ['
            for i in ind_data.index.values:
                tw_data += f"{(ind_data.loc[i, self.date_col] - initial_date).days} " \
                           f"{ind_data.loc[i, self.weight_col]}; "
            my_data_code += tw_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{ind_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_UNITS}; " \
                            f"label.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_LABELS};\n"

            my_data_code += f"units.{self.TYPE}_{ind_id} = {self.UNITS}; " \
                            + f"label.{self.TYPE}_{ind_id} = {self.LABELS}; " \
                            + f"txtData.title.{self.TYPE}_{ind_id} = 'Growth curve of individual {ind_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{ind_id} = '{self.comment}, individual {ind_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{ind_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class FinalWeightIndDataSource(IndDataSourceBase):
    TYPE = 'Wf'

    def __init__(self, csv_filename, id_col, weight_col, age_col, date_col,
                 name=None, bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name)
        self.weight_col = weight_col
        self.age_col = age_col
        self.date_col = date_col
        self.bibkey = bibkey
        self.comment = comment

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.individuals)

        units = "{'d', 'kg'}"
        labels = "{'Final wet weight'}"
        my_data_code = f'%% Final Weight data \n\n'
        for animal_id in ind_list:
            if animal_id not in self.individuals:
                continue
            animal_data = self.get_ind_data(animal_id).sort_values(by=self.age_col)
            initial_weight = animal_data.iloc[0][self.weight_col]
            final_weight = animal_data.iloc[-1][self.weight_col]
            duration = animal_data.iloc[-1][self.age_col] - animal_data.iloc[0][self.age_col]

            my_data_code += f'data.{self.TYPE}_{animal_id} = {final_weight}; '
            my_data_code += f"init.{self.TYPE}_{animal_id} = [{duration} ,{initial_weight}]; " \
                            f"units.init.{self.TYPE}_{animal_id} = {units}; " \
                            f"label.init.{self.TYPE}_{animal_id} = 'Time elapsed and initial weight';\n"

            my_data_code += f"units.{self.TYPE}_{animal_id} = 'kg'; " \
                            + f"label.{self.TYPE}_{animal_id} = {labels}; " \
                            + f"txtData.title.{self.TYPE}_{animal_id} = 'Final weight of individual {animal_id}'; "

            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{animal_id} = '{self.comment}, individual {animal_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{animal_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeFeedIndDataSource(IndDataSourceBase):
    TYPE = "tJX"
    UNITS = "{'d', 'kg'}"
    LABELS = "{'Time since start', 'Daily food consumption'}"
    AUX_DATA_UNITS = "'kg'"
    AUX_DATA_LABELS = "'Initial weight'"

    def __init__(self, csv_filename, id_col, feed_col, date_col, weight_data_source: TimeWeightDataSource,
                 start_at_first=False, name=None, bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name)
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, ind_id):
        ind_data = self.get_ind_data(ind_id).sort_values(by=self.date_col)

        ind_weight_data = self.weight_data.get_ind_data(ind_id).copy()

        if self.start_at_first:
            ind_weight_data = ind_weight_data.sort_values(by=self.weight_data.date_col)
            initial_date = ind_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = ind_weight_data.iloc[0][self.weight_data.weight_col]
        else:
            # Get weight measurement closest to the first feed intake
            ind_weight_data['diff'] = (ind_weight_data[self.weight_data.date_col] - ind_data.iloc[0][self.date_col]) \
                .apply(lambda d: d.days - 1)
            ind_weight_data = ind_weight_data[ind_weight_data['diff'] < 0].sort_values('diff', ascending=False)
            initial_date = ind_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = ind_weight_data.iloc[0][self.weight_data.weight_col]

        return ind_data, initial_date, initial_weight

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.individuals)

        my_data_code = f'%% Time vs Daily feed consumption data\n\n'
        for ind_id in ind_list:
            if ind_id not in self.individuals:
                continue

            ind_data, initial_date, initial_weight = self.get_data(ind_id)

            t_JX_data = f'data.{self.TYPE}_{ind_id} = ['
            for i in ind_data.index.values:
                t_JX_data += f"{(ind_data.loc[i, self.date_col] - initial_date).days} " \
                             f"{ind_data.loc[i, self.feed_col]}; "
            my_data_code += t_JX_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{ind_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_UNITS}; " \
                            f"label.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_LABELS};\n"

            my_data_code += f"units.{self.TYPE}_{ind_id} = {self.UNITS}; " \
                            + f"label.{self.TYPE}_{ind_id} = {self.LABELS}; " \
                            + f"txtData.title.{self.TYPE}_{ind_id} = 'Daily feed consumption of individual {ind_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{ind_id} = '{self.comment}, individual {ind_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{ind_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeCumulativeFeedIndDataSource(IndDataSourceBase):
    TYPE = "tCX"
    UNITS = "{'d', 'kg'}"
    LABELS = "{'Time since start', 'Cumulative food consumption during test'}"
    AUX_DATA_UNITS = "'kg'"
    AUX_DATA_LABELS = "'Initial weight'"

    def __init__(self, csv_filename, id_col, feed_col, date_col, weight_data_source: TimeWeightDataSource,
                 name=None, bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name)
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.individuals)

        my_data_code = f'%% Time vs Cumulative Feed Consumption data\n\n'
        for ind_id in ind_list:
            if ind_id not in self.individuals:
                continue
            ind_data = self.get_ind_data(ind_id).sort_values(by=self.date_col)
            initial_date = ind_data.iloc[0][self.date_col]

            ind_weight_data = self.weight_data.get_ind_data(ind_id).copy()
            ind_weight_data['diff'] = (ind_weight_data[self.weight_data.date_col] - initial_date) \
                .apply(lambda d: d.days - 1)
            ind_weight_data = ind_weight_data[ind_weight_data['diff'] < 0].sort_values('diff', ascending=False)

            closest_values = ind_weight_data.sort_values(by='diff').iloc[:2][
                [self.weight_data.date_col, self.weight_data.weight_col]] \
                .sort_values(by=self.weight_data.date_col).values
            if len(closest_values) == 1:
                d1, initial_weight = closest_values[0]
            elif len(closest_values) == 2:
                (d1, w1), (d2, w2) = closest_values
                initial_weight = round((w2 - w1) / (d2 - d1).days * ((initial_date - d1).days - 1) + w1)
            else:
                raise Exception("No weight measurement before first feed intake")
            tCX_data = f'data.{self.TYPE}_{ind_id} = [0 0; '
            for i in ind_data.index.values:
                tCX_data += f"{(ind_data.loc[i, self.date_col] - initial_date).days + 1} " \
                            f"{ind_data.loc[i, self.feed_col]}; "
            my_data_code += tCX_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{ind_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_UNITS}; " \
                            f"label.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_LABELS};\n"

            my_data_code += f"units.{self.TYPE}_{ind_id} = {self.UNITS}; " \
                            + f"label.{self.TYPE}_{ind_id} = {self.LABELS}; " \
                            + f"txtData.title.{self.TYPE}_{ind_id} = 'Food consumption of individual {ind_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{ind_id} = '{self.comment}, individual {ind_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{ind_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class GroupTimeFeedDataSource(GroupDataSourceBase):
    TYPE = 'tJX_grp'
    UNITS = "{'d', 'kg'}"
    LABELS = "{'Time since start', 'Daily food consumption of group during test'}"
    AUX_DATA_UNITS = "{'kg'}"
    AUX_DATA_LABELS = "{'Initial weights for the individuals in the group'}"

    def __init__(self, csv_filename, group_col, feed_col, date_col, weight_data_source: TimeWeightDataSource,
                 name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename, group_col, name=name, prefix=prefix)
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source
        self.weight_data.df[self.group_col] = self.weight_data.df[self.group_col].astype('str')
        if self.prefix:
            self.weight_data.df[self.group_col] = f"{self.prefix}_" + self.weight_data.df[self.group_col]
        self.create_group_of_ind_df(self.weight_data)

    def get_data(self, group_id):
        group_data = self.get_group_data(group_id).sort_values(by=self.date_col)

        initial_dates = []
        initial_weights = {}
        for ind_id in self.get_ind_list_of_group(group_id):
            ind_weight_data = self.weight_data.get_ind_data(ind_id).copy()
            ind_weight_data['diff'] = (ind_weight_data[self.weight_data.date_col] -
                                       group_data.iloc[0][self.date_col]).apply(lambda d: d.days - 1)
            ind_weight_data = ind_weight_data[ind_weight_data['diff'] < 0].sort_values('diff', ascending=False)
            initial_weights[ind_id] = ind_weight_data.iloc[0][self.weight_data.weight_col]
            initial_dates.append(ind_weight_data.iloc[0][self.weight_data.date_col])

        return group_data, initial_dates, initial_weights

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.weight_data.individuals)
        group_list = self.get_groups_in_ind_list(ind_list)

        my_data_code = f'%% Time vs Group daily feed consumption data\n\n'
        for group_id in group_list:
            if group_id not in self.groups:
                continue
            # Get initial weights, assumes all weight measurements were taken on the same day for the individuals in the
            # group
            group_data, initial_dates, initial_weights = self.get_data(group_id)

            t_JX_group_data = f'data.{self.TYPE}_{group_id} = ['
            for i in group_data.index.values:
                t_JX_group_data += f"{(group_data.loc[i, self.date_col] - initial_dates[0]).days} " \
                                   f"{group_data.loc[i, self.feed_col]}; "
            my_data_code += t_JX_group_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{group_id} = {format_dict_data(initial_weights)}; " \
                            f"units.init.{self.TYPE}_{group_id} = {self.AUX_DATA_UNITS}; " \
                            f"label.init.{self.TYPE}_{group_id} = {self.AUX_DATA_LABELS};\n"

            my_data_code += f"units.{self.TYPE}_{group_id} = {self.UNITS}; " \
                            + f"label.{self.TYPE}_{group_id} = {self.LABELS}; " \
                            + f"txtData.title.{self.TYPE}_{group_id} = 'Daily feed consumption of pen {group_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{group_id} = '{self.comment}, pen {group_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{group_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeCH4DataSource(IndDataSourceBase):
    TYPE = 'tCH4'
    UNITS = "{'d', 'g/d'}"
    LABELS = "{'Time since start', 'Daily methane (CH4) emissions'}"
    AUX_DATA_UNITS = "'kg'"
    AUX_DATA_LABELS = "'Initial weight'"

    def __init__(self, csv_filename, id_col, methane_col, date_col, weight_data_source: TimeWeightDataSource,
                 start_at_first=False, name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name, prefix=prefix)
        self.methane_col = methane_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, ind_id):
        ind_data = self.get_ind_data(ind_id).sort_values(by=self.date_col)
        ind_weight_data = self.weight_data.get_ind_data(ind_id).copy()

        if self.start_at_first:
            ind_weight_data = ind_weight_data.sort_values(by=self.weight_data.date_col)
            initial_date = ind_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = ind_weight_data.iloc[0][self.weight_data.weight_col]
        else:
            # Get weight measurement closest to the first methane measurement
            ind_weight_data['diff'] = (ind_weight_data[self.weight_data.date_col] - ind_data.iloc[0][self.date_col]) \
                .apply(lambda d: d.days - 1)
            ind_weight_data = ind_weight_data[ind_weight_data['diff'] < 0].sort_values('diff', ascending=False)
            initial_date = ind_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = ind_weight_data.iloc[0][self.weight_data.weight_col]

        return ind_data, initial_date, initial_weight

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.individuals)

        my_data_code = f'%% Time vs Daily methane (CH4) emissions data\n\n'
        for ind_id in ind_list:
            if ind_id not in self.individuals:
                continue

            ind_data, initial_date, initial_weight = self.get_data(ind_id)

            tCH4_data = f'data.{self.TYPE}_{ind_id} = ['
            for i in ind_data.index.values:
                tCH4_data += f"{(ind_data.loc[i, self.date_col] - initial_date).total_seconds() / (60 * 60 * 24):.2f}" \
                             f" {ind_data.loc[i, self.methane_col]}; "
            my_data_code += tCH4_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{ind_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_UNITS}; " \
                            f"label.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_LABELS};\n"

            my_data_code += f"units.{self.TYPE}_{ind_id} = {self.UNITS}; " \
                            + f"label.{self.TYPE}_{ind_id} = {self.LABELS}; " \
                            + f"txtData.title.{self.TYPE}_{ind_id} = 'Daily CH4 emissions of individual {ind_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{ind_id} = '{self.comment}, individual {ind_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{ind_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeCO2DataSource(IndDataSourceBase):
    TYPE = 'tCO2'
    UNITS = "{'d', 'g/d'}"
    LABELS = "{'Time since start', 'Daily carbon dioxide (CO2) emissions'}"
    AUX_DATA_UNITS = "'kg'"
    AUX_DATA_LABELS = "'Initial weight'"

    def __init__(self, csv_filename, id_col, co2_col, date_col, weight_data_source: TimeWeightDataSource,
                 start_at_first=False, name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name, prefix=prefix)
        self.co2_col = co2_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, ind_id):
        ind_data = self.get_ind_data(ind_id).sort_values(by=self.date_col)
        ind_weight_data = self.weight_data.get_ind_data(ind_id).copy()

        if self.start_at_first:
            ind_weight_data = ind_weight_data.sort_values(by=self.weight_data.date_col)
            initial_date = ind_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = ind_weight_data.iloc[0][self.weight_data.weight_col]
        else:
            # Get weight measurement closest to the first methane measurement
            ind_weight_data['diff'] = (ind_weight_data[self.weight_data.date_col] - ind_data.iloc[0][self.date_col]) \
                .apply(lambda d: d.days - 1)
            ind_weight_data = ind_weight_data[ind_weight_data['diff'] < 0].sort_values('diff', ascending=False)
            initial_date = ind_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = ind_weight_data.iloc[0][self.weight_data.weight_col]

        return ind_data, initial_date, initial_weight

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.individuals)

        my_data_code = f'%% Time vs Daily carbon dioxide (CO2) emissions data\n\n'
        for ind_id in ind_list:
            if ind_id not in self.individuals:
                continue

            ind_data, initial_date, initial_weight = self.get_data(ind_id)

            tCO2_data = f'data.{self.TYPE}_{ind_id} = ['
            for i in ind_data.index.values:
                tCO2_data += f"{(ind_data.loc[i, self.date_col] - initial_date).total_seconds() / (60 * 60 * 24):.2f}" \
                             f" {ind_data.loc[i, self.co2_col]}; "
            my_data_code += tCO2_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{ind_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_UNITS}; " \
                            f"label.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_LABELS};\n"

            my_data_code += f"units.{self.TYPE}_{ind_id} = {self.UNITS}; " \
                            + f"label.{self.TYPE}_{ind_id} = {self.LABELS}; " \
                            + f"txtData.title.{self.TYPE}_{ind_id} = 'Daily CO2 emissions of individual {ind_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{ind_id} = '{self.comment}, individual {ind_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{ind_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class WeightFeedIndDataSource(IndDataSourceBase):
    # TODO: Update with last changes
    TYPE = 'WCX'

    def __init__(self, csv_filename, id_col, weight_col, feed_col, date_col,
                 name=None, bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name)
        self.bibkey = bibkey
        self.comment = comment
        self.weight_col = weight_col
        self.feed_col = feed_col
        self.date_col = date_col

    def generate_code(self, ind_list='all'):
        # TODO: retry to check that the first value has zero food consumption
        # TODO: Add a fix for when the first value is not zero
        if ind_list == 'all':
            ind_list = list(self.individuals)

        groups = self.df.groupby(self.id_col)

        my_data_code = f'%% Weight vs Cumulative Feed Consumption data\n\n'
        for animal_id in ind_list:
            if animal_id not in self.individuals:
                continue
            animal_data = groups.get_group(animal_id)
            animal_data.sort_values(by='age', inplace=True)
            initial_weight = animal_data.iloc[0][self.weight_col]

            WCX_data = f'data.{self.TYPE}_{animal_id} = ['
            for i in animal_data.index.values:
                WCX_data += f"{animal_data.loc[i, self.weight_col]} {animal_data.loc[i, self.feed_col]}; "
            my_data_code += WCX_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{animal_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{animal_id} = 'kg'; " \
                            f"label.init.{self.TYPE}_{animal_id} = 'Initial weight';\n"
            units = "{'kg', 'kg'}"
            labels = "{'Weight', 'Cumulative food consumption during test'}"
            my_data_code += f"units.{self.TYPE}_{animal_id} = {units}; " \
                            + f"label.{self.TYPE}_{animal_id} = {labels}; " \
                            + f"txtData.title.{self.TYPE}_{animal_id} = 'Food consumption vs weight of animal {animal_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{animal_id} = '{self.comment}, animal {animal_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{animal_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TotalFeedIntakeIndDataSource(IndDataSourceBase):
    # TODO: Update with last changes
    TYPE = 'TFI'

    def __init__(self, csv_filename, id_col, feed_col, age_col, date_col, weight_data_source: TimeWeightDataSource,
                 name=None, bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name)
        self.feed_col = feed_col
        self.age_col = age_col
        self.date_col = date_col
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.individuals)

        extra_data_units = "{'d', 'kg'}"
        labels = "{'Total feed intake'}"
        my_data_code = f'%% Total feed intake data \n\n'
        for animal_id in ind_list:
            if animal_id not in self.individuals:
                continue
            animal_data = self.get_ind_data(animal_id).sort_values(by=self.age_col)
            duration = animal_data.iloc[-1][self.age_col] - animal_data.iloc[0][self.age_col] + 1
            total_feed_intake = animal_data.iloc[-1][self.feed_col]

            animal_weights = self.weight_data.get_ind_data(animal_id).sort_values(by=self.weight_data.age_col)
            initial_weight = animal_weights.iloc[0][self.weight_data.weight_col]

            my_data_code += f'data.{self.TYPE}_{animal_id} = {total_feed_intake}; '
            my_data_code += f"init.{self.TYPE}_{animal_id} = [{duration} ,{initial_weight}]; " \
                            f"units.init.{self.TYPE}_{animal_id} = {extra_data_units}; " \
                            f"label.init.{self.TYPE}_{animal_id} = 'Time elapsed and initial weight';\n"

            my_data_code += f"units.{self.TYPE}_{animal_id} = 'kg'; " \
                            + f"label.{self.TYPE}_{animal_id} = {labels}; " \
                            + f"txtData.title.{self.TYPE}_{animal_id} = 'Total feed intake of animal {animal_id}'; "

            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{animal_id} = '{self.comment}, animal {animal_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{animal_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeMilkIndDataSource(IndDataSourceBase):
    TYPE = 'tJL'
    UNITS = "{'d', 'L/d'}"
    LABELS = "{'Time since start', 'Milk production per day'}"

    def __init__(self, csv_filename, id_col, milk_col, day_col,
                 name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name, prefix=prefix)
        self.milk_col = milk_col
        self.day_col = day_col
        self.bibkey = bibkey
        self.comment = comment

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.individuals)

        my_data_code = f'%% Time vs Milk production data \n\n'
        for ind_id in ind_list:
            if ind_id not in self.individuals:
                continue
            ind_data = self.get_ind_data(ind_id).sort_values(by=self.day_col)
            tmilk_data = f'data.{self.TYPE}_{ind_id} = ['
            for i in ind_data.index.values:
                tmilk_data += f"{ind_data.loc[i, self.day_col]} " \
                              f"{ind_data.loc[i, self.milk_col]}; "
            my_data_code += tmilk_data[:-2] + '];\n'

            my_data_code += f"units.{self.TYPE}_{ind_id} = {self.UNITS}; " \
                            + f"label.{self.TYPE}_{ind_id} = {self.LABELS}; " \
                            + f"txtData.title.{self.TYPE}_{ind_id} = 'Milk production curve of individual {ind_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{ind_id} = '{self.comment}, individual {ind_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{ind_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class AgeWeightIndDataSource(IndDataSourceBase):
    TYPE = "aW"
    UNITS = "{'d', 'kg'}"
    LABELS = "{'Age since birth', 'Wet weight'}"
    AUX_DATA_UNITS = "'-'"
    AUX_DATA_LABELS = "'Number of twins'"

    def __init__(self, csv_filename, id_col, weight_col, age_col, n_twins_col,
                 name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name, prefix=prefix)
        self.weight_col = weight_col
        self.age_col = age_col
        self.n_twins_col = n_twins_col
        self.bibkey = bibkey
        self.comment = comment

    def generate_code(self, ind_list='all'):
        if ind_list == 'all':
            ind_list = list(self.individuals)

        my_data_code = f'%% Age vs Weight data \n\n'
        for ind_id in ind_list:
            if ind_id not in self.individuals:
                continue
            ind_data = self.get_ind_data(ind_id).sort_values(by=self.age_col)
            n_twins = ind_data.iloc[0][self.n_twins_col]
            aw_data = f'data.{self.TYPE}_{ind_id} = ['
            for i in ind_data.index.values:
                aw_data += f"{ind_data.loc[i, self.age_col]} " \
                           f"{ind_data.loc[i, self.weight_col]}; "
            my_data_code += aw_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{ind_id} = {n_twins}; " \
                            f"units.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_UNITS}; " \
                            f"label.init.{self.TYPE}_{ind_id} = {self.AUX_DATA_LABELS};\n"

            my_data_code += f"units.{self.TYPE}_{ind_id} = {self.UNITS}; " \
                            + f"label.{self.TYPE}_{ind_id} = {self.LABELS}; " \
                            + f"txtData.title.{self.TYPE}_{ind_id} = 'Age weight curve of individual {ind_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{ind_id} = '{self.comment}, individual {ind_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{ind_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code
