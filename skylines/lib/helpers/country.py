from flask.ext.babel import get_locale

__all__ = ['country_name', 'country_name', 'language_to_country_code']

__conversion_dict = {
    'en': 'gb',
    'ja': 'jp',
    'nb': 'no',
    'sv': 'se',
    'zh_TW': 'cn',
    'zh_Hant_TW': 'cn',
    'cs': 'cz',
    'sl': 'si',
}


def country_name(code):
    return get_locale().territories[code.upper()]


def language_to_country_code(language):
    return __conversion_dict.get(language, language)
