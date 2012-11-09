from __future__ import absolute_import
from pycountry import countries

__all__ = ['country_name']


def country_name(code):
    return countries.get(alpha2=code).name

