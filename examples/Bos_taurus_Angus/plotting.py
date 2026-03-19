import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import timedelta as td

f = 1
T_A = 8000
T_ref = 20 + 273.15
T = 38.6 + 273.15
TC = np.exp(T_A / T_ref - T_A / T)
d_E = 0.3
w_E = 23.9
mu_E = 550_000
w_X = 23.9
mu_X = 525_000

end_date = pd.to_datetime('2023-03-27')

axis_limits = {
    'tW': (400, 750),
    'tJX_grp': (20, 70),
}


def set_date_ticks(ax, num_ticks, start_date, end_date):
    """
    Set a specified number of date ticks on the given axis between start_date and end_date.

    Parameters:
    - ax: The axis object to set the ticks on.
    - start_date: The start date (as a datetime object or a string in 'YYYY-MM-DD' format).
    - end_date: The end date (as a datetime object or a string in 'YYYY-MM-DD' format).
    - num_ticks: The number of ticks to set, including the start and end dates.
    """
    # Convert start_date and end_date to pandas Timestamp if they are not already
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    time_interval = td(days=(end_date - start_date).days / (num_ticks - 1))
    xticks = [start_date + i * time_interval for i in range(num_ticks)]

    # Set the ticks and format them
    ax.set_xticks(xticks)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.set_xlabel('')


def weight_curve(pars, t, W_init):
    ome = pars['p_Am'] / pars['v'] * w_E / d_E / mu_E
    L_inf = f * pars['p_Am'] * pars['kap'] / pars['p_M']
    r_B = TC * pars['p_M'] / 3 / (pars['E_G'] + f * pars['kap'] * pars['p_Am'] / pars['v'])

    L_init = np.cbrt(W_init * 1e3 / (1 + f * ome))
    L = L_inf - (L_inf - L_init) * np.exp(-t * r_B)
    return (1 + f * ome) * L ** 3 / 1e3


def plot_weight(ax, data_source, data_tier, data_entity_id, pars, pars_tier, pars_entity_id, tier_structure):
    ind_data, initial_date, initial_weight = data_source.get_data(data_entity_id)
    sns.scatterplot(data=ind_data, x=data_source.date_col, y=data_source.weight_col, ax=ax, label='Data')

    t = np.linspace(0, (end_date - initial_date).days, 100)
    dates = [initial_date + td(days=ti) for ti in t]
    weight = weight_curve(pars, t, W_init=initial_weight)
    ax.plot(dates, weight, label='DEB Model', color='red')

    set_date_ticks(ax, 5, start_date=dates[0], end_date=dates[-1])
    ax.legend()
    ax.grid()
    ax.set_ylabel(f'Weight [{data_source._units[-1]}]')
    ax.set_title(f'{pars_entity_id} -- {data_entity_id}')
    # ax.set_xlim(start_date, end_date)
    ax.set_ylim(axis_limits['tW'])


def feed_intake_curve(pars, t, W_init):
    ome = pars['p_Am'] / pars['v'] * w_E / d_E / mu_E
    L_inf = f * pars['p_Am'] * pars['kap'] / pars['p_M']
    r_B = TC * pars['p_M'] / 3 / (pars['E_G'] + f * pars['kap'] * pars['p_Am'] / pars['v'])
    a_JX = f * w_X * pars['p_Am'] * TC / mu_X / pars['kap_X']

    L_init = np.cbrt(W_init * 1e3 / (1 + f * ome))
    L = L_inf - (L_inf - L_init) * np.exp(-t * r_B)
    JX = a_JX * L ** 2 / 1e3
    return JX


def plot_group_feed_intake(ax, data_source, data_tier, data_group_id, data_entity_pars_dict, pars_tier,
                           pars_entity_list, tier_structure):
    group_data, initial_dates, initial_weights = data_source.get_data(data_group_id)
    sns.scatterplot(data=group_data, x=data_source.date_col, y=data_source.feed_col, ax=ax, label='Data')

    t = np.linspace(0, (end_date - initial_dates[0]).days, 100)
    dates = [initial_dates[0] + td(days=ti) for ti in t]
    pen_feed_intake = np.zeros_like(t)
    for ind_id, pars in data_entity_pars_dict.items():
        pen_feed_intake += feed_intake_curve(pars=pars, t=t, W_init=initial_weights[ind_id])
    ax.plot(dates, pen_feed_intake, label='DEB model', color='red')
    set_date_ticks(ax, 5, start_date=dates[0], end_date=dates[-1])
    ax.legend()
    ax.grid()
    ax.set_xlabel('')
    ax.set_ylabel(f'Pen feed intake [{data_source._units[-1]}]')
    ax.set_ylim(axis_limits['tJX_grp'])
    ax.set_title(data_group_id)
