from tg.i18n import get_lang
from babel.core import Locale, UnknownLocaleError

__all__ = ['get_locale']


def get_locale():
    locales = get_lang()
    if locales is not None:
        for locale in locales:
            try:
                locale = Locale.parse(locale)
                return locale
            except UnknownLocaleError:
                pass

    return Locale('en')
