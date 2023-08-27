import pandas_datareader as pdr
import pandas as pd
import datetime
from .utils import get_window_start_date

__ALL__ = [
    'get_famafrench_factor_timeseries',
    'get_famafrench_performance_grid'
]


def get_famafrench_factor_timeseries(
    start_date=datetime.date(1900, 1, 1),
    end_date=pd.Timestamp.max.normalize().to_pydatetime(),
    factors_type='3_factors',
    frequency='daily'
):
    if factors_type == '3_factors':
        dataset_type = 'F-F_Research_Data_Factors_daily'
    elif factors_type == '5_factors':
        dataset_type = 'F-F_Research_Data_5_Factors_2x3_daily'
    else:
        raise ValueError(f'factors_type provided: {factors_type} is not valid')

    datasets = pdr.get_data_famafrench(dataset_type, start=start_date, end=end_date)
    datasets = datasets[0]

    additional_datasets = [
        'F-F_ST_Reversal_Factor_daily',
        'F-F_LT_Reversal_Factor_daily',
        'F-F_Momentum_Factor_daily'
    ]

    for _additional_dataset in additional_datasets:
        _datasets = pdr.get_data_famafrench(_additional_dataset, start=start_date, end=end_date)
        _datasets = _datasets[0]
        datasets = datasets.join(_datasets)

    datasets = datasets.div(100)

    if frequency == 'weekly':
        datasets = datasets.resample('W-MON', label='left', closed='left').apply(lambda s: s.add(1).prod().add(-1))
    elif frequency == 'monthly':
        datasets = datasets.resample('MS', label='left', closed='left').apply(lambda s: s.add(1).prod().add(-1))
    elif frequency == 'quarterly':
        datasets = datasets.resample('QS', label='left', closed='left').apply(lambda s: s.add(1).prod().add(-1))
    elif frequency == 'yearly':
        datasets = datasets.resample('AS', label='left', closed='right').apply(lambda s: s.add(1).prod().add(-1))

    return datasets


def get_famafrench_performance_grid(
    portfolio='size+value',
    window='QTD'
):
    start_date = datetime.date(1900, 1, 1)
    end_date = pd.Timestamp.max.normalize().to_pydatetime()

    if portfolio == 'size+value':
        dataset_type = '6_Portfolios_2x3_daily'
    else:
        raise ValueError(f'Parameter portfolio provided: {portfolio} is not yet implemented.')

    datasets = pdr.get_data_famafrench(dataset_type, start=start_date, end=end_date)
    datasets = datasets[0] # value weighted.
    datasets = datasets.div(100)

    latest_date = datasets.index[-1]

    window_start_date = get_window_start_date(latest_date, window)
    datasets_window_returns = datasets.loc[window_start_date:latest_date].add(1).prod().add(-1)

    returns_table = pd.DataFrame({
        'Returns': datasets_window_returns.values,
        'Size': ['SMALL']*3 + ['BIG']*3,
        'Style': ['Growth', 'Mid', 'Value']*2
    }).pivot_table(index='Style', columns='Size')

    returns_table.columns = returns_table.columns.get_level_values(1)

    return returns_table


