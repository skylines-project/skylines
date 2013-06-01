from __future__ import absolute_import

from flask.ext.babel import get_locale
import babel.numbers

__all__ = ['format_number', 'format_decimal']


def format_number(*args, **kw):
    return babel.numbers.format_number(*args, locale=get_locale(), **kw)


def format_decimal(*args, **kw):
    return babel.numbers.format_decimal(*args, locale=get_locale(), **kw)
