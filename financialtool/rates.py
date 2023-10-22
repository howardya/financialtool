import pandas_datareader as pdr
# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
from .utils import convert_tenor_to_days, get_window_start_date

FRED_TENORS = pd.DataFrame({
    'Tenor': ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y'],
    'Ticker': ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'DGS20', 'DGS30'],
    'Country': ['US'] * 11
})


def get_yield_historical_data(tenors=None, country='US'):
    if tenors is None:
        tenors_tickers = FRED_TENORS.query(f'Country=="{country}"')['Ticker']
    else:
        if type(tenors) is not list:
            tenors = [tenors]
        tenors_tickers = FRED_TENORS[FRED_TENORS['Tenor'].isin(tenors)].query(f'Country=="{country}"')['Ticker']

    rates_data = pdr.get_data_fred(tenors_tickers, datetime.datetime(1900, 1, 1))
    rates_data.index = rates_data.index.to_pydatetime()

    rates_data.columns = FRED_TENORS.set_index('Ticker').loc[rates_data.columns]['Tenor'].to_list()

    return rates_data

def get_yield_curve(country='US', dates=None, append_latest=True, plot=False, plot_slope=True):
    if country != 'US':
        raise ValueError(f'country provided: {country} not yet implemented.')

    if dates is None:
        dates = []
    elif type(dates) != list:
        dates = [dates]

    if append_latest:
        dates.append(datetime.date.today())

    dates_original = dates.copy()

    dates = [x if type(x) != str else get_window_start_date(pd.to_datetime(datetime.datetime.today()), x) for x in dates_original]

    end_date = max(dates)
    start_date = min(dates) - datetime.timedelta(20)

    rates_data = pdr.get_data_fred(FRED_TENORS['Ticker'], start_date, end_date)
    rates_data.index = rates_data.index.to_pydatetime()
    rates_data = rates_data.dropna()

    dates_closest = [rates_data.index[np.argmin(np.abs(rates_data.index - pd.to_datetime(date)).days)] for date in dates]
    dates_closest_index = [i[0] for i in sorted(enumerate(dates_closest), key=lambda x: x[1])]

    dates_closest = [dates_closest[i] for i in dates_closest_index]

    rates_data = rates_data.loc[dates_closest]
    rates_data = rates_data.transpose()

    tenor_list = FRED_TENORS.set_index('Ticker').loc[rates_data.index].loc[:, 'Tenor'].tolist()
    tenor_in_days = convert_tenor_to_days(tenor_list)

    rates_data.index = tenor_in_days

    dates_string = [x.strftime('%d-%m-%Y') for x in dates_closest]
    dates_string_addon = [f'({x})' if type(x) == str else '' for x in dates_original]
    dates_string_addon = [dates_string_addon[i] for i in dates_closest_index]
    dates_string = [dates_string[j] + dates_string_addon[j] for j in range(len(dates_string_addon))]
    rates_data.columns = dates_string

    if plot:
        ax = rates_data.plot(title=f'Yield Curve - {country}')
        _ = ax.set_xticks(tenor_in_days)
        x_labels = tenor_list.copy()
        x_labels[1] = None
        x_labels[2] = None
        _ = ax.set_xticklabels(x_labels)

        if plot_slope:
            slope_data = rates_data.loc[pd.Series(tenor_in_days, index=tenor_list)[['2Y', '10Y']].to_list()].copy()
            for line in ax.get_lines():
                color = line.get_color()
                label = line.get_label()
                points_x = slope_data.index.to_list()
                points_y = slope_data[label].to_list()
                ax.plot(points_x, points_y, linestyle='--', color=color, alpha=0.4)

    return rates_data, tenor_list, tenor_in_days

