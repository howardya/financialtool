import datetime
def get_window_start_date(current_date, window):
    day = current_date.day
    month = current_date.month
    year = current_date.year
    dayofweek = current_date.dayofweek # monday is 0

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
    else:
        raise ValueError(f'Argument window: {window} not yet implemented.')

    return datetime.date(year, month, day)

