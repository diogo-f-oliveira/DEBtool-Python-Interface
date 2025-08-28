from .base import EntityDataSourceBase
import pandas as pd


class TimeWeightEntityDataSource(EntityDataSourceBase):
    TYPE = "tW"
    LABELS = ('Time since start', 'Wet weight')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, weight_col, date_col, name=None,
                 prefix='', bibkey='', comment='',
                 time_unit='d', weight_unit='kg',
                 ):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name,
                         prefix=prefix, bibkey=bibkey, comment=comment,
                         ind_var_unit=time_unit, dep_var_unit=weight_unit, aux_var_unit=weight_unit)
        self.weight_col = weight_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])

    def get_data(self, entity_id):
        ind_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)
        initial_weight = ind_data.iloc[0][self.weight_col]
        initial_date = ind_data.iloc[0][self.date_col]
        return ind_data, initial_date, initial_weight

    def generate_mydata_code(self, entity_list='all'):
        # TODO: Check if this is needed
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = ''
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue
            ind_data, initial_date, initial_weight = self.get_data(entity_id)

            tw_data = f'data.{self.TYPE}_{entity_id} = ['
            for i in ind_data.index.values:
                tw_data += f"{(ind_data.loc[i, self.date_col] - initial_date).days} " \
                           f"{ind_data.loc[i, self.weight_col]}; "
            my_data_code += tw_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{entity_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{entity_id} = {self.aux_data_units}; " \
                            f"label.init.{self.TYPE}_{entity_id} = {self.aux_data_labels};\n"

            my_data_code += f"units.{self.TYPE}_{entity_id} = {self.units}; " \
                            + f"label.{self.TYPE}_{entity_id} = {self.labels}; " \
                            + f"title.{self.TYPE}_{entity_id} = 'Growth curve of individual {entity_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{entity_id} = '{self.comment}, individual {entity_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{entity_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        if len(my_data_code):
            my_data_code = '%% Time vs Weight data \n\n' + my_data_code

        return my_data_code


# Deprecated
class FinalWeightEntityDataSource(EntityDataSourceBase):
    # TODO: Update with latest changes
    TYPE = 'Wf'

    def __init__(self, csv_filename, id_col, weight_col, age_col, date_col,
                 name=None, bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name)
        self.weight_col = weight_col
        self.age_col = age_col
        self.date_col = date_col
        self.bibkey = bibkey
        self.comment = comment

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        units = "{'d', 'kg'}"
        labels = "{'Final wet weight'}"
        my_data_code = f'%% Final Weight data \n\n'
        for animal_id in entity_list:
            if animal_id not in self.entities:
                continue
            animal_data = self.get_entity_data(animal_id).sort_values(by=self.age_col)
            initial_weight = animal_data.iloc[0][self.weight_col]
            final_weight = animal_data.iloc[-1][self.weight_col]
            duration = animal_data.iloc[-1][self.age_col] - animal_data.iloc[0][self.age_col]

            my_data_code += f'data.{self.TYPE}_{animal_id} = {final_weight}; '
            my_data_code += f"init.{self.TYPE}_{animal_id} = [{duration} ,{initial_weight}]; " \
                            f"units.init.{self.TYPE}_{animal_id} = {units}; " \
                            f"label.init.{self.TYPE}_{animal_id} = 'Time elapsed and initial weight';\n"

            my_data_code += f"units.{self.TYPE}_{animal_id} = 'kg'; " \
                            + f"label.{self.TYPE}_{animal_id} = {labels}; " \
                            + f"title.{self.TYPE}_{animal_id} = 'Final weight of individual {animal_id}'; "

            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{animal_id} = '{self.comment}, individual {animal_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{animal_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeFeedEntityDataSource(EntityDataSourceBase):
    TYPE = "tJX"
    LABELS = ('Time since start', 'Daily food consumption')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, feed_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 start_at_first=False, prefix='', name=None, bibkey='', comment='', time_unit='d', feed_unit='kg'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, ind_var_unit=time_unit, dep_var_unit=feed_unit,
                         aux_var_unit=weight_data_source._units[1])
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, entity_id):
        ind_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)

        ind_weight_data = self.weight_data.get_entity_data(entity_id).copy()

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

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = f'%% Time vs Daily feed consumption data\n\n'
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue

            ind_data, initial_date, initial_weight = self.get_data(entity_id)

            t_JX_data = f'data.{self.TYPE}_{entity_id} = ['
            for i in ind_data.index.values:
                t_JX_data += f"{(ind_data.loc[i, self.date_col] - initial_date).days} " \
                             f"{ind_data.loc[i, self.feed_col]}; "
            my_data_code += t_JX_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{entity_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{entity_id} = {self.aux_data_units}; " \
                            f"label.init.{self.TYPE}_{entity_id} = {self.aux_data_labels};\n"

            my_data_code += f"units.{self.TYPE}_{entity_id} = {self.units}; " \
                            + f"label.{self.TYPE}_{entity_id} = {self.labels}; " \
                            + f"title.{self.TYPE}_{entity_id} = 'Daily feed consumption of individual {entity_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{entity_id} = '{self.comment}, individual {entity_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{entity_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeCumulativeFeedEntityDataSource(EntityDataSourceBase):
    TYPE = "tCX"
    LABELS = ('Time since start', 'Cumulative food consumption during test')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, feed_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 prefix='', name=None, bibkey='', comment='', time_unit='d', feed_unit='kg'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, ind_var_unit=time_unit, dep_var_unit=feed_unit,
                         aux_var_unit=weight_data_source._units[1])
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.weight_data = weight_data_source

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = f'%% Time vs Cumulative Feed Consumption data\n\n'
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue
            ind_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)
            initial_date = ind_data.iloc[0][self.date_col]

            ind_weight_data = self.weight_data.get_entity_data(entity_id).copy()
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
            tCX_data = f'data.{self.TYPE}_{entity_id} = [0 0; '
            for i in ind_data.index.values:
                tCX_data += f"{(ind_data.loc[i, self.date_col] - initial_date).days + 1} " \
                            f"{ind_data.loc[i, self.feed_col]}; "
            my_data_code += tCX_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{entity_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{entity_id} = {self.aux_data_units}; " \
                            f"label.init.{self.TYPE}_{entity_id} = {self.aux_data_labels};\n"

            my_data_code += f"units.{self.TYPE}_{entity_id} = {self.units}; " \
                            + f"label.{self.TYPE}_{entity_id} = {self.labels}; " \
                            + f"title.{self.TYPE}_{entity_id} = 'Food consumption of individual {entity_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{entity_id} = '{self.comment}, individual {entity_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{entity_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeCH4EntityDataSource(EntityDataSourceBase):
    TYPE = 'tCH4'
    LABELS = ('Time since start', 'Daily methane (CH4) emissions')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, methane_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 start_at_first=False, name=None, prefix='', bibkey='', comment='', time_unit='d', methane_unit='g/d'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, ind_var_unit=time_unit, dep_var_unit=methane_unit,
                         aux_var_unit=weight_data_source._units[1])

        self.methane_col = methane_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, entity_id):
        ind_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)
        ind_weight_data = self.weight_data.get_entity_data(entity_id).copy()

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

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = f'%% Time vs Daily methane (CH4) emissions data\n\n'
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue

            ind_data, initial_date, initial_weight = self.get_data(entity_id)

            tCH4_data = f'data.{self.TYPE}_{entity_id} = ['
            for i in ind_data.index.values:
                tCH4_data += f"{(ind_data.loc[i, self.date_col] - initial_date).total_seconds() / (60 * 60 * 24):.2f}" \
                             f" {ind_data.loc[i, self.methane_col]}; "
            my_data_code += tCH4_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{entity_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{entity_id} = {self.aux_data_units}; " \
                            f"label.init.{self.TYPE}_{entity_id} = {self.aux_data_labels};\n"

            my_data_code += f"units.{self.TYPE}_{entity_id} = {self.units}; " \
                            + f"label.{self.TYPE}_{entity_id} = {self.labels}; " \
                            + f"title.{self.TYPE}_{entity_id} = 'Daily CH4 emissions of individual {entity_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{entity_id} = '{self.comment}, individual {entity_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{entity_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeCO2EntityDataSource(EntityDataSourceBase):
    TYPE = 'tCO2'
    LABELS = ('Time since start', 'Daily carbon dioxide (CO2) emissions')
    AUX_DATA_LABELS = 'Initial weight'

    def __init__(self, csv_filename, id_col, co2_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 start_at_first=False, name=None, prefix='', bibkey='', comment='', time_unit='d', co2_unit='g/d'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, ind_var_unit=time_unit, dep_var_unit=co2_unit,
                         aux_var_unit=weight_data_source._units[1])

        self.co2_col = co2_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
        self.weight_data = weight_data_source
        self.start_at_first = start_at_first

    def get_data(self, entity_id):
        ind_data = self.get_entity_data(entity_id).sort_values(by=self.date_col)
        ind_weight_data = self.weight_data.get_entity_data(entity_id).copy()

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

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = f'%% Time vs Daily carbon dioxide (CO2) emissions data\n\n'
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue

            ind_data, initial_date, initial_weight = self.get_data(entity_id)

            tCO2_data = f'data.{self.TYPE}_{entity_id} = ['
            for i in ind_data.index.values:
                tCO2_data += f"{(ind_data.loc[i, self.date_col] - initial_date).total_seconds() / (60 * 60 * 24):.2f}" \
                             f" {ind_data.loc[i, self.co2_col]}; "
            my_data_code += tCO2_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{entity_id} = {initial_weight}; " \
                            f"units.init.{self.TYPE}_{entity_id} = {self.aux_data_units}; " \
                            f"label.init.{self.TYPE}_{entity_id} = {self.aux_data_labels};\n"

            my_data_code += f"units.{self.TYPE}_{entity_id} = {self.units}; " \
                            + f"label.{self.TYPE}_{entity_id} = {self.labels}; " \
                            + f"title.{self.TYPE}_{entity_id} = 'Daily CO2 emissions of individual {entity_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{entity_id} = '{self.comment}, individual {entity_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{entity_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


# Deprecated
class WeightFeedEntityDataSource(EntityDataSourceBase):
    # TODO: Update with latest changes
    TYPE = 'WCX'

    def __init__(self, csv_filename, id_col, weight_col, feed_col, date_col,
                 name=None, bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name)
        self.bibkey = bibkey
        self.comment = comment
        self.weight_col = weight_col
        self.feed_col = feed_col
        self.date_col = date_col

    def generate_mydata_code(self, entity_list='all'):
        # TODO: retry to check that the first value has zero food consumption
        # TODO: Add a fix for when the first value is not zero
        if entity_list == 'all':
            entity_list = list(self.entities)

        groups = self.df.groupby(self.id_col)

        my_data_code = f'%% Weight vs Cumulative Feed Consumption data\n\n'
        for animal_id in entity_list:
            if animal_id not in self.entities:
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
                            + f"title.{self.TYPE}_{animal_id} = 'Food consumption vs weight of animal {animal_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{animal_id} = '{self.comment}, animal {animal_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{animal_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


# Deprecated
class TotalFeedIntakeEntityDataSource(EntityDataSourceBase):
    # TODO: Update with latest changes
    TYPE = 'TFI'

    def __init__(self, csv_filename, id_col, feed_col, age_col, date_col, weight_data_source: TimeWeightEntityDataSource,
                 name=None, bibkey='', comment=''):
        super().__init__(csv_filename, id_col, name=name)
        self.feed_col = feed_col
        self.age_col = age_col
        self.date_col = date_col
        self.bibkey = bibkey
        self.comment = comment
        self.weight_data = weight_data_source

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        extra_data_units = "{'d', 'kg'}"
        labels = "{'Total feed intake'}"
        my_data_code = f'%% Total feed intake data \n\n'
        for animal_id in entity_list:
            if animal_id not in self.entities:
                continue
            animal_data = self.get_entity_data(animal_id).sort_values(by=self.age_col)
            duration = animal_data.iloc[-1][self.age_col] - animal_data.iloc[0][self.age_col] + 1
            total_feed_intake = animal_data.iloc[-1][self.feed_col]

            animal_weights = self.weight_data.get_entity_data(animal_id).sort_values(by=self.weight_data.age_col)
            initial_weight = animal_weights.iloc[0][self.weight_data.weight_col]

            my_data_code += f'data.{self.TYPE}_{animal_id} = {total_feed_intake}; '
            my_data_code += f"init.{self.TYPE}_{animal_id} = [{duration} ,{initial_weight}]; " \
                            f"units.init.{self.TYPE}_{animal_id} = {extra_data_units}; " \
                            f"label.init.{self.TYPE}_{animal_id} = 'Time elapsed and initial weight';\n"

            my_data_code += f"units.{self.TYPE}_{animal_id} = 'kg'; " \
                            + f"label.{self.TYPE}_{animal_id} = {labels}; " \
                            + f"title.{self.TYPE}_{animal_id} = 'Total feed intake of animal {animal_id}'; "

            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{animal_id} = '{self.comment}, animal {animal_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{animal_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class TimeMilkEntityDataSource(EntityDataSourceBase):
    TYPE = 'tJL'
    LABELS = ('Time since start', 'Milk production per day')

    def __init__(self, csv_filename, id_col, milk_col, day_col, name=None, prefix='', bibkey='', comment='',
                 time_unit='d', milk_unit='L/d'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, ind_var_unit=time_unit, dep_var_unit=milk_unit)
        self.milk_col = milk_col
        self.day_col = day_col

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = f'%% Time vs Milk production data \n\n'
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue
            ind_data = self.get_entity_data(entity_id).sort_values(by=self.day_col)
            tmilk_data = f'data.{self.TYPE}_{entity_id} = ['
            for i in ind_data.index.values:
                tmilk_data += f"{ind_data.loc[i, self.day_col]} " \
                              f"{ind_data.loc[i, self.milk_col]}; "
            my_data_code += tmilk_data[:-2] + '];\n'

            my_data_code += f"units.{self.TYPE}_{entity_id} = {self.units}; " \
                            + f"label.{self.TYPE}_{entity_id} = {self.labels}; " \
                            + f"title.{self.TYPE}_{entity_id} = 'Milk production curve of individual {entity_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{entity_id} = '{self.comment}, individual {entity_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{entity_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code


class AgeWeightTwinsEntityDataSource(EntityDataSourceBase):
    TYPE = "aW"
    # TODO: Check if this is supposed to be time since birth, age since birth is a misnomer
    LABELS = ('Age since birth', 'Wet weight')
    AUX_DATA_LABELS = 'Number of twins'

    def __init__(self, csv_filename, id_col, weight_col, age_col, n_twins_col, name=None, prefix='', bibkey='',
                 comment='', age_unit='d', weight_unit='kg'):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment, ind_var_unit=age_unit, dep_var_unit=weight_unit, aux_var_unit='#')
        self.weight_col = weight_col
        self.age_col = age_col
        self.n_twins_col = n_twins_col

    def generate_mydata_code(self, entity_list='all'):
        if entity_list == 'all':
            entity_list = list(self.entities)

        my_data_code = f'%% Age vs Weight data \n\n'
        for entity_id in entity_list:
            if entity_id not in self.entities:
                continue
            ind_data = self.get_entity_data(entity_id).sort_values(by=self.age_col)
            n_twins = ind_data.iloc[0][self.n_twins_col]
            aw_data = f'data.{self.TYPE}_{entity_id} = ['
            for i in ind_data.index.values:
                aw_data += f"{ind_data.loc[i, self.age_col]} " \
                           f"{ind_data.loc[i, self.weight_col]}; "
            my_data_code += aw_data[:-2] + '];\n'
            my_data_code += f"init.{self.TYPE}_{entity_id} = {n_twins}; " \
                            f"units.init.{self.TYPE}_{entity_id} = {self.aux_data_units}; " \
                            f"label.init.{self.TYPE}_{entity_id} = {self.aux_data_labels};\n"

            my_data_code += f"units.{self.TYPE}_{entity_id} = {self.units}; " \
                            + f"label.{self.TYPE}_{entity_id} = {self.labels}; " \
                            + f"title.{self.TYPE}_{entity_id} = 'Age weight curve of individual {entity_id}'; "
            if self.comment:
                my_data_code += f"comment.{self.TYPE}_{entity_id} = '{self.comment}, individual {entity_id}'; "
            if self.bibkey:
                my_data_code += f"bibkey.{self.TYPE}_{entity_id} = '{self.bibkey}';"
            my_data_code += '\n\n'

        return my_data_code
