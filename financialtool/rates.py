import pandas_datareader as pdr
import pandas as pd
import numpy as np
import datetime
from .utils import convert_tenor_to_days

FRED_TENORS = pd.DataFrame({
    'Tenor': ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y'],
    'Ticker': ['DGS1MO', 'DGS3MO', 'DGS6MO', 'DGS1', 'DGS2', 'DGS3', 'DGS5', 'DGS7', 'DGS10', 'DGS20', 'DGS30'],
    'Country': ['US'] * 11
})


def get_yield_curve(country='US', dates=None):
    if country != 'US':
        raise ValueError(f'country provided: {country} not yet implemented.')

    if dates is None:
        dates = [datetime.date.today()]
    elif type(dates) != list:
        dates = [dates]

    end_date = max(dates)
    start_date = min(dates) - datetime.timedelta(20)

    rates_data = pdr.get_data_fred(FRED_TENORS['Ticker'], start_date, end_date)
    rates_data.index = rates_data.index.to_pydatetime()
    rates_data = rates_data.dropna()

    rates_closest = [rates_data.index[np.argmin(np.abs(rates_data.index - pd.to_datetime(date)).days)] for date in dates]
    rates_closest.sort()

    rates_data = rates_data.loc[rates_closest]
    rates_data = rates_data.transpose()

    tenor_list = FRED_TENORS.set_index('Ticker').loc[rates_data.index].loc[:, 'Tenor'].tolist()
    tenor_in_days = convert_tenor_to_days(tenor_list)

    rates_data.index = tenor_in_days

    ax = rates_data.plot()
    ax.set_xticks(tenor_in_days)
    x_labels = tenor_list.copy()
    x_labels[1] = None
    x_labels[2] = None
    ax.set_xticklabels(x_labels)

    return rates_data, tenor_list, ax

