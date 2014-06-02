from flask import current_app, request
from flask.ext.babel import get_locale

import GeoIP

__all__ = ['country_name', 'country_name', 'language_to_country_code', 'country_from_ip']

__conversion_dict = {
    'en': 'gb',
    'ja': 'jp',
    'nb': 'no',
    'sv': 'se',
    'zh_TW': 'cn',
    'zh_Hant_TW': 'cn',
    'cs': 'cz',
}


def country_name(code):
    return get_locale().territories[code.upper()]


def language_to_country_code(language):
    return __conversion_dict.get(language, language)


def country_from_ip():
    geoip = GeoIP.open(current_app.config.get('GEOIP_DATABASE'), GeoIP.GEOIP_STANDARD)
    return geoip.country_code_by_addr(request.remote_addr)
