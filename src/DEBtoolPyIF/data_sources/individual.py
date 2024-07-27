from .base import IndDataSourceBase
import pandas as pd


class TimeWeightDataSource(IndDataSourceBase):
    TYPE = "tW"
    UNITS = "{'d', 'kg'}"
    LABELS = "{'Time since start', 'Wet weight'}"
    AUX_DATA_UNITS = "'kg'"
    AUX_DATA_LABELS = "'Initial weight'"

    def __init__(self, csv_filename, id_col, weight_col, date_col, name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment)
        self.weight_col = weight_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])

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


# Deprecated
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
                 start_at_first=False, prefix='', name=None, bibkey='', comment=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment)
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
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
                 prefix='', name=None, bibkey='', comment=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment)
        self.feed_col = feed_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
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


class TimeCH4DataSource(IndDataSourceBase):
    TYPE = 'tCH4'
    UNITS = "{'d', 'g/d'}"
    LABELS = "{'Time since start', 'Daily methane (CH4) emissions'}"
    AUX_DATA_UNITS = "'kg'"
    AUX_DATA_LABELS = "'Initial weight'"

    def __init__(self, csv_filename, id_col, methane_col, date_col, weight_data_source: TimeWeightDataSource,
                 start_at_first=False, name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment)
        self.methane_col = methane_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
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
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment)
        self.co2_col = co2_col
        self.date_col = date_col
        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
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


# Deprecated
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


# Deprecated
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

    def __init__(self, csv_filename, id_col, milk_col, day_col, name=None, prefix='', bibkey='', comment=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment)
        self.milk_col = milk_col
        self.day_col = day_col

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

    def __init__(self, csv_filename, id_col, weight_col, age_col, n_twins_col, name=None, prefix='', bibkey='',
                 comment=''):
        super().__init__(csv_filename=csv_filename, id_col=id_col, name=name, prefix=prefix, bibkey=bibkey,
                         comment=comment)
        self.weight_col = weight_col
        self.age_col = age_col
        self.n_twins_col = n_twins_col

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
