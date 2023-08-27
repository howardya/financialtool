import datetime
import numpy as np

def get_window_start_date(current_date, window):
    day = current_date.day
    month = current_date.month
    year = current_date.year
    dayofweek = current_date.dayofweek # monday is 0
    days_to_go_back = 0

    if window == 'QTD':
        day = 1
        if month <= 3:
            month = 1
        elif month <= 6:
            month = 4
        elif month <= 9:
            month = 7
        else:
            month = 10
    elif window == 'MTD':
        day = 1
    elif window == 'WTD':
        days_to_go_back = dayofweek
    elif window == 'YTD':
        day = 1
        month = 1
    elif window == 'T-1':
        days_to_go_back = 1
    elif window == 'T-1B':
        if dayofweek == 0: # Monday
            days_to_go_back = 3
        elif dayofweek == 6: # Sunday
            days_to_go_back = 2
        elif dayofweek == 5:  # Saturday
            days_to_go_back = 1
    else:
        raise ValueError(f'Argument window: {window} not yet implemented.')

    start_date = datetime.date(year, month, day)
    start_date = start_date + datetime.timedelta(-days_to_go_back)

    return start_date


def convert_tenor_to_days(tenors):
    if type(tenors) != list:
        tenors = [tenors]

    tenors_in_days = []
    for tenor in tenors:
        tenor_unit = tenor[-1]
        try:
            tenor_in_unit = float(tenor[:-1])
        except:
            tenor_in_unit = np.nan

        if tenor_unit == 'Y':
            multiplier = 365
        elif tenor_unit == 'Q':
            multiplier = 365/4
        elif tenor_unit == 'M':
            multiplier = 30
        elif tenor_unit == 'W':
            multiplier = 7
        elif tenor_unit == 'D':
            multiplier = 1
        else:
            raise ValueError(f'tenor unit {tenor_unit} not yet implemented.')

        tenors_in_days.append(tenor_in_unit * multiplier)

    if len(tenors_in_days) == 1:
        tenors_in_days = tenors_in_days[0]

    return tenors_in_days