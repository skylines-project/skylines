# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context, request
from tg.i18n import get_lang
from babel import parse_locale
from babel.util import distinct

from skylines.config.i18n import languages, language_info
from skylines.model import Notification


__all__ = ['BaseController']


class BaseController(TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)

    def _before(self, *args, **kw):
        def get_primary_languages():
            available = [lang['language_code'] for lang in languages()]
            requested = distinct(get_lang() or ['en'])

            # add primary languages
            primary = []
            for language in requested:
                if language in available:
                    primary.append(language)
                else:
                    try:
                        locale = parse_locale(language)
                    except:
                        continue

                    if locale[0] in available:
                        primary.append(locale[0])

            if len(primary) == 0:
                return [language_info('en')]

            return [language_info(lang) for lang in distinct(primary)]

        tmpl_context.available_languages = languages()

        tmpl_context.primary_languages = get_primary_languages()
        tmpl_context.secondary_languages = [lang for lang in tmpl_context.available_languages if lang not in tmpl_context.primary_languages]

        tmpl_context.current_language = tmpl_context.primary_languages[0]

        if request.identity:
            request.identity['notifications'] = Notification.count_unread(request.identity['user'])
