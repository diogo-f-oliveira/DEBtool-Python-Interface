import numpy as np

from .base import EntityDataSourceBase, ZeroVariateEntityDataSource
from ..utils.data_conversion import convert_numeric_array_to_matlab
import pandas as pd


class TimeWeightEntityDataSource(EntityDataSourceBase):
    TYPE = "tW"
    LABELS = ('Time since start', 'Wet weight')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, weight_col, date_col, name=None,
                 prefix='', bibkey='', comment='', title='', id_name='',
                 time_unit='d', weight_unit='kg',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=weight_col, dep_var_unit=weight_unit,
                         indep_var_col=date_col, indep_var_unit=time_unit,
                         # TODO: Think of another way to do this?
                         aux_datasource=self,
                         prefix=prefix, bibkey=bibkey, comment=comment, title=title, id_name=id_name,
                         )
        self.weight_col = weight_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])

    # TODO: Rename to avoid confusion with get_entity_data
    def get_data(self, entity_id):
        entity_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)
        initial_weight = entity_data.iloc[0][self.weight_col]
        initial_date = entity_data.iloc[0][self.date_col]
        return entity_data, initial_date, initial_weight

    def generate_mydata_code(self, entity_list='all'):
        # TODO: Check if this is needed
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = ''
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue
            entity_data, initial_date, initial_weight = self.get_data(entity_id)

            time_data = entity_data[self.date_col].apply(lambda x: (x - initial_date).days).values
            weight_data = entity_data[self.weight_col].values
            data = np.column_stack([time_data, weight_data])

            my_data_code += self.generate_dataset_code(id_=entity_id, data=data, converted_aux_data=initial_weight,
                                                       auxdata_struct_name='init')
            my_data_code += '\n\n'

        if my_data_code:
            my_data_code = '%% Time vs Weight data \n\n' + my_data_code

        return my_data_code


class WeightEntityDataSource(ZeroVariateEntityDataSource):
    TYPE = "Ww"
    LABELS = 'Wet weight'

    def __init__(self, csv_filename, id_col, weight_col, name=None,
                 prefix='', bibkey='', comment='', id_name='',
                 weight_unit='kg',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=weight_col, dep_var_unit=weight_unit,
                         prefix=prefix, bibkey=bibkey, comment=comment, id_name=id_name,
                         )
        self.weight_col = weight_col

# Deprecated
# TODO: Update dependent, independent and aux data arguments
class TimeFeedEntityDataSource(EntityDataSourceBase):
    TYPE = "tJX"
    LABELS = ('Time since start', 'Daily food consumption')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, feed_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 start_at_first=False, prefix='', name=None, bibkey='', comment='', time_unit='d', feed_unit='kg'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, indep_var_unit=time_unit, dep_var_unit=feed_unit,
                         aux_var_unit=weight_data_source._units[1])
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, entity_id):
        entity_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)

        entity_weight_data = self.weight_data.get_entity_data(entity_id).copy()

        if self.start_at_first:
            entity_weight_data = entity_weight_data.sort_values(by=self.weight_data.date_col)
            initial_date = entity_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = entity_weight_data.iloc[0][self.weight_data.weight_col]
        else:
            # Get weight measurement closest to the first feed intake
            entity_weight_data['diff'] = (
                    entity_weight_data[self.weight_data.date_col] - entity_data.iloc[0][self.date_col]) \
                .apply(lambda d: d.days - 1)
            entity_weight_data = entity_weight_data[entity_weight_data['diff'] < 0].sort_values('diff', ascending=False)
            initial_date = entity_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = entity_weight_data.iloc[0][self.weight_data.weight_col]

        return entity_data, initial_date, initial_weight

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = f'%% Time vs Daily feed consumption data\n\n'
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue

            entity_data, initial_date, initial_weight = self.get_data(entity_id)

            time_data = entity_data[self.date_col].apply(lambda x: (x - initial_date).days).values
            feed_data = entity_data[self.feed_col].values
            data = np.column_stack([time_data, feed_data])

            my_data_code += self.generate_dataset_code(id_=entity_id, data=data, converted_aux_data=initial_weight,
                                                       auxdata_struct_name='init')
            my_data_code += '\n\n'

        return my_data_code


class TimeCH4EntityDataSource(EntityDataSourceBase):
    TYPE = 'tCH4'
    LABELS = ('Time since start', 'Daily methane (CH4) emissions')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, methane_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 start_at_first=False, name=None, prefix='', bibkey='', comment='', title='', id_name='',
                 time_unit='d', methane_unit='g/d'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=methane_col, dep_var_unit=methane_unit,
                         indep_var_col=date_col, indep_var_unit=time_unit,
                         aux_datasource=weight_data_source,
                         prefix=prefix, bibkey=bibkey,
                         comment=comment, title=title, id_name=id_name,
                         )

        self.methane_col = methane_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, entity_id):
        entity_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)
        entity_weight_data = self.weight_data.get_entity_data(entity_id).copy()

        if self.start_at_first:
            entity_weight_data = entity_weight_data.sort_values(by=self.weight_data.date_col)
            initial_date = entity_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = entity_weight_data.iloc[0][self.weight_data.weight_col]
        else:
            # Get weight measurement closest to the first methane measurement
            entity_weight_data['diff'] = (
                    entity_weight_data[self.weight_data.date_col] - entity_data.iloc[0][self.date_col]) \
                .apply(lambda d: d.days - 1)
            entity_weight_data = entity_weight_data[entity_weight_data['diff'] < 0].sort_values('diff', ascending=False)
            initial_date = entity_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = entity_weight_data.iloc[0][self.weight_data.weight_col]

        return entity_data, initial_date, initial_weight

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = ''
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue

            entity_data, initial_date, initial_weight = self.get_data(entity_id)

            time_data = entity_data[self.date_col].apply(lambda d: (d - initial_date).total_seconds() / (60 * 60 * 24))
            ch4_data = entity_data[self.methane_col].values
            data = np.column_stack([time_data, ch4_data])

            my_data_code += self.generate_dataset_code(id_=entity_id, data=data, converted_aux_data=initial_weight,
                                                       auxdata_struct_name='init')
            my_data_code += '\n\n'

        if my_data_code:
            my_data_code = f'%% Time vs Daily methane (CH4) emissions data\n\n' + my_data_code

        return my_data_code


class TimeCO2EntityDataSource(EntityDataSourceBase):
    TYPE = 'tCO2'
    LABELS = ('Time since start', 'Daily carbon dioxide (CO2) emissions')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, co2_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 start_at_first=False, name=None, prefix='', bibkey='', comment='', title='', id_name='',
                 time_unit='d', co2_unit='g/d'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=co2_col, dep_var_unit=co2_unit,
                         indep_var_col=date_col, indep_var_unit=time_unit,
                         aux_datasource=weight_data_source,
                         prefix=prefix, bibkey=bibkey,
                         comment=comment, title=title, id_name=id_name,
                         )

        self.co2_col = co2_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, entity_id):
        entity_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)
        entity_weight_data = self.weight_data.get_entity_data(entity_id).copy()

        if self.start_at_first:
            entity_weight_data = entity_weight_data.sort_values(by=self.weight_data.date_col)
            initial_date = entity_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = entity_weight_data.iloc[0][self.weight_data.weight_col]
        else:
            # Get weight measurement closest to the first methane measurement
            entity_weight_data['diff'] = (
                    entity_weight_data[self.weight_data.date_col] - entity_data.iloc[0][self.date_col]) \
                .apply(lambda d: d.days - 1)
            entity_weight_data = entity_weight_data[entity_weight_data['diff'] < 0].sort_values('diff', ascending=False)
            initial_date = entity_weight_data.iloc[0][self.weight_data.date_col]
            initial_weight = entity_weight_data.iloc[0][self.weight_data.weight_col]

        return entity_data, initial_date, initial_weight

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = ''
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue

            entity_data, initial_date, initial_weight = self.get_data(entity_id)

            time_data = entity_data[self.date_col].apply(lambda d: (d - initial_date).total_seconds() / (60 * 60 * 24))
            ch4_data = entity_data[self.co2_col].values
            data = np.column_stack([time_data, ch4_data])

            my_data_code += self.generate_dataset_code(id_=entity_id, data=data, converted_aux_data=initial_weight,
                                                       auxdata_struct_name='init')
            my_data_code += '\n\n'

        if my_data_code:
            my_data_code = f'%% Time vs Daily carbon dioxide (CO2) emissions data\n\n' + my_data_code

        return my_data_code


# TODO: Update dependent, independent and aux data arguments
class TimeMilkEntityDataSource(EntityDataSourceBase):
    TYPE = 'tJL'
    LABELS = ('Time since start', 'Milk production per day')

    def __init__(self, csv_filename, id_col, milk_col, day_col, name=None, prefix='', bibkey='', comment='',
                 title='', id_name='', time_unit='d', milk_unit='L/d'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, title=title, id_name=id_name, indep_var_unit=time_unit,
                         dep_var_unit=milk_unit)
        self.milk_col = milk_col
        self.day_col = day_col

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = ''
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue
            entity_data = self.get_entity_data(entity_id).sort_values(by=self.day_col)

            data = entity_data[[self.day_col, self.milk_col]].values

            my_data_code += self.generate_dataset_code(id_=entity_id, data=data)

            my_data_code += '\n\n'

        if my_data_code:
            my_data_code = f'%% Time vs Milk production data \n\n' + my_data_code

        return my_data_code


# TODO: Update dependent, independent and aux data arguments
class AgeWeightTwinsEntityDataSource(EntityDataSourceBase):
    TYPE = "aW"
    # TODO: Check if this is supposed to be time since birth, age since birth is a misnomer
    LABELS = ('Age since birth', 'Wet weight')
    AUX_DATA_LABELS = 'Number of twins'

    def __init__(self, csv_filename, id_col, weight_col, age_col, n_twins_col, name=None, prefix='', bibkey='',
                 comment='', title='', id_name='', age_unit='d', weight_unit='kg'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, title=title, id_name=id_name,
                         indep_var_unit=age_unit, dep_var_unit=weight_unit, aux_var_unit='#')
        self.weight_col = weight_col
        self.age_col = age_col
        self.n_twins_col = n_twins_col

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = ''
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue
            entity_data = self.get_entity_data(entity_id).sort_values(by=self.age_col)
            data = entity_data[[self.age_col, self.weight_col]].values
            n_twins = entity_data.iloc[0][self.n_twins_col]

            my_data_code += self.generate_dataset_code(id_=entity_id, data=data, converted_aux_data=n_twins,
                                                       auxdata_struct_name='init')

            my_data_code += '\n\n'

        if my_data_code:
            my_data_code = '%% Age vs Weight data \n\n' + my_data_code

        return my_data_code


class DigestibilityEntityDataSource(ZeroVariateEntityDataSource):
    TYPE = 'DMD'
    LABELS = 'Digestibility'

    def __init__(self, csv_filename, id_col, dmd_col, name=None, prefix='', bibkey='', comment='',
                 unit='-', id_name=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         dep_var_col=dmd_col, dep_var_unit=unit,
                         prefix=prefix, bibkey=bibkey,
                         comment=comment, id_name=id_name)
        self.dmd_col = dmd_col

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = ''
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue
            data = self.get_entity_data(entity_id)
            # data = entity_data[self.dmd_col].values

            my_data_code += self.generate_dataset_code(id_=entity_id, data=data)

            my_data_code += '\n\n'

        if my_data_code:
            my_data_code = f'%% Dry matter digestibility data \n\n' + my_data_code

        return my_data_code
