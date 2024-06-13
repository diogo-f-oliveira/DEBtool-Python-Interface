from .base import GroupDataSourceBase
from .individual import TimeWeightDataSource
from ..utils.data_formatter import format_dict_data
import pandas as pd


class GroupTimeFeedDataSource(GroupDataSourceBase):
    TYPE = 'tJX_grp'
    UNITS = "{'d', 'kg'}"
    LABELS = "{'Time since start', 'Daily food consumption of group during test'}"
    AUX_DATA_UNITS = "{'kg'}"
    AUX_DATA_LABELS = "{'Initial weights for the individuals in the group'}"

    def __init__(self, csv_filename, id_col, feed_col, date_col, weight_data_source: TimeWeightDataSource,
                 name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment)
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source
        self.weight_data.df[self.id_col] = self.weight_data.df[self.id_col].astype('str')
        if self.prefix:
            self.weight_data.df[self.id_col] = f"{self.prefix}_" + self.weight_data.df[self.id_col]
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
