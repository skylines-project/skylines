from __future__ import absolute_import
from babel import Locale
from tg import tmpl_context

__all__ = ['country_name', 'language_to_country_code']

__conversion_dict = {'en': 'gb',
                     'ja': 'jp',
                     'sv': 'se'}

def country_name(code):
    locale = Locale(tmpl_context.current_language['language_code'])
    return locale.territories[code.upper()]


def language_to_country_code(language):
    if language in __conversion_dict:
        return __conversion_dict[language]
    else:
        return language
