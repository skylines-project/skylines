from __future__ import absolute_import
from pycountry import countries

__all__ = ['country_name', 'language_to_country_code']

__conversion_dict = {'en': 'gb',
                     'ja': 'jp',
                     'sv': 'se'}

def country_name(code):
    return countries.get(alpha2=code.upper()).name

def language_to_country_code(language):
    if language in __conversion_dict:
        return __conversion_dict[language]
    else:
        return language
