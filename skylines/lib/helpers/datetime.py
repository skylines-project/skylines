from __future__ import absolute_import
from datetime import timedelta

__all__ = ['isoformat_utc', 'format_timedelta']


def isoformat_utc(dt):
    return dt.isoformat() + 'Z'


def format_timedelta(delta):
    if isinstance(delta, timedelta):
        seconds = delta.total_seconds()
    else:
        seconds = delta

    return '%d:%02d' % (seconds / 3600, seconds % 3600 / 60)
