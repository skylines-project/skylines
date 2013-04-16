import os

from tg import config
from babel import Locale

from skylines.lib.helpers.country import language_to_country_code

__all__ = ['language_info', 'update', 'languages']

__languages = []


def language_info(language):
    country_code = language_to_country_code(language)
    locale = Locale.parse(language)
    local_name = locale.display_name.capitalize()
    english_name = locale.english_name.capitalize()

    return dict(language_code=language,
                country_code=country_code,
                local_name=local_name,
                english_name=english_name)


def update():
    global __languages

    i18n_path = os.path.join(config['pylons.paths']['root'], 'i18n')

    __languages = []
    for fname in os.listdir(i18n_path):
        path = os.path.join(i18n_path, fname)
        if os.path.isdir(path):
            __languages.append(language_info(fname))

    __languages.sort(key=lambda lang: lang['local_name'])

    return __languages


def languages():
    return __languages
