from __future__ import absolute_import

from datetime import datetime, time, timedelta


def from_seconds_of_day(date, seconds_of_day):
    seconds_of_day = timedelta(seconds=seconds_of_day)
    return datetime.combine(date, time(0, 0, 0)) + seconds_of_day
