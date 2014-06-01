from __future__ import absolute_import

from datetime import datetime, time, timedelta, date


def from_seconds_of_day(date, seconds_of_day):
    seconds_of_day = timedelta(seconds=seconds_of_day)
    return datetime.combine(date, time(0, 0, 0)) + seconds_of_day


def to_seconds_of_day(start_date, time):
    if isinstance(start_date, datetime):
        delta = time - start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif isinstance(start_date, date):
        delta = time - datetime(year=start_date.year, month=start_date.month, day=start_date.day)
    else:
        raise ValueError

    return delta.total_seconds()
