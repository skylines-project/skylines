from __future__ import absolute_import

import babel.dates
from babel.core import Locale, UnknownLocaleError
from datetime import timedelta
from tg.i18n import get_lang

__all__ = ['isoformat_utc',
           'format_date', 'format_time', 'format_datetime',
           'format_timedelta']


def get_locale():
    locales = get_lang()
    if locales is not None:
        for locale in locales:
            try:
                locale = Locale.parse(locale)
                return locale
            except UnknownLocaleError:
                pass

    return 'en'


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
