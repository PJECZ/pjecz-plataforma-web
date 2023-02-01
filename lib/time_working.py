"""
Tiempo Laboral
"""
from datetime import date, timedelta


def next_labor_day(in_date: date, days: int = 1):
    """Next labor day from in_date considering days"""
    out_date = in_date
    for i in range(days):
        out_date += timedelta(days=1)
        # Skip weekends
        while out_date.weekday() in [5, 6]:
            out_date += timedelta(days=1)
        # TODO: Skip holidays
    return out_date
