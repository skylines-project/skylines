from babel import Locale
from tg import tmpl_context
from flask.ext.babel import get_locale

__all__ = ['country_name', 'country_name_flask', 'language_to_country_code']

__conversion_dict = {
    'en': 'gb',
    'ja': 'jp',
    'nb': 'no',
    'sv': 'se',
    'zh_TW': 'cn',
    'cs': 'cz',
}


def country_name(code):
    locale = Locale(tmpl_context.current_language['language_code'])
    return locale.territories[code.upper()]


def country_name_flask(code):
    return get_locale().territories[code.upper()]


def language_to_country_code(language):
    return __conversion_dict.get(language, language)
