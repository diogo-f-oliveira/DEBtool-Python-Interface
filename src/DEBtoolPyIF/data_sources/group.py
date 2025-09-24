import numpy as np

from .base import GroupDataSourceBase
from .entity import TimeWeightEntityDataSource
from ..utils.data_conversion import convert_dict_to_matlab
import pandas as pd


class TimeFeedGroupDataSource(GroupDataSourceBase):
    TYPE = 'tJX_grp'
    LABELS = ('Time since start', 'Daily food consumption of group during test')
    AUX_DATA_LABELS = ('Initial weights for the individuals in the group')

    def __init__(self, csv_filename, id_col, feed_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 name=None, time_unit='d', feed_unit='kg',
                 prefix='', bibkey='', comment='', title='', id_name=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=feed_col, dep_var_unit=feed_unit,
                         indep_var_col=date_col, indep_var_unit=time_unit,
                         aux_datasource=weight_data_source,
                         prefix=prefix, bibkey=bibkey,
                         comment=comment, title=title, id_name=id_name,
                         )
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source
        self.weight_data.df[self.id_col] = self.weight_data.df[self.id_col].astype('str')
        if self.prefix:
            self.weight_data.df[self.id_col] = f"{self.prefix}_" + self.weight_data.df[self.id_col]
        self.create_entity_vs_group_df(self.weight_data)

    def get_data(self, group_id):
        group_data = self.get_group_data(group_id).sort_values(by=self.date_col)

        initial_dates = []
        initial_weights = {}
        for entity_id in self.get_entity_list_of_group(group_id):
            ind_weight_data = self.weight_data.get_entity_data(entity_id).copy()
            ind_weight_data['diff'] = (ind_weight_data[self.weight_data.date_col] -
                                       group_data.iloc[0][self.date_col]).apply(lambda d: d.days - 1)
            ind_weight_data = ind_weight_data[ind_weight_data['diff'] < 0].sort_values('diff', ascending=False)
            initial_weights[entity_id] = ind_weight_data.iloc[0][self.weight_data.weight_col]
            initial_dates.append(ind_weight_data.iloc[0][self.weight_data.date_col])

        return group_data, initial_dates, initial_weights

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.weight_data.entities)
        group_list = self.get_groups_in_entity_list(entity_list)

        my_data_code = ''
        for group_id in group_list:
            if group_id not in self.groups:
                continue
            # Get initial weights, assumes all weight measurements were taken on the same day for the individuals in the
            # group
            group_data, initial_dates, initial_weights = self.get_data(group_id)

            time_data = group_data[self.date_col].apply(lambda x: (x - initial_dates[0]).days).values
            feed_data = group_data[self.feed_col].values
            data = np.column_stack([time_data, feed_data])

            conv_aux_data = convert_dict_to_matlab(initial_weights)
            my_data_code += self.generate_dataset_code(id_=group_id, data=data, converted_aux_data=conv_aux_data,
                                                       auxdata_struct_name='init')

            my_data_code += '\n\n'

        if len(my_data_code):
            my_data_code = '%% Time vs Group daily feed consumption data\n\n' + my_data_code

        return my_data_code
