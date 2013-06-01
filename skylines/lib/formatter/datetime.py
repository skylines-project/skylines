from __future__ import absolute_import

from datetime import timedelta

from flask.ext.babel import get_locale
import babel.dates

__all__ = ['isoformat_utc',
           'format_date', 'format_time', 'format_datetime',
           'format_timedelta']


def isoformat_utc(dt):
    return dt.isoformat() + 'Z'


def format_date(*args, **kw):
    return babel.dates.format_date(*args, locale=get_locale(), **kw)


def format_time(*args, **kw):
    return babel.dates.format_time(*args, locale=get_locale(), **kw)


def format_datetime(*args, **kw):
    return babel.dates.format_datetime(*args, locale=get_locale(), **kw)


def format_timedelta(delta):
    if isinstance(delta, timedelta):
        seconds = delta.total_seconds()
    else:
        seconds = delta

    return '%d:%02d' % (seconds / 3600, seconds % 3600 / 60)
