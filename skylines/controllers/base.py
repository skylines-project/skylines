# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context, request, redirect, url
from tg.i18n import get_lang, sanitize_language_code
from skylines.config.i18n import languages, language_info
from babel.util import distinct
from babel import parse_locale

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
            available_languages = [lang['language_code'] for lang in languages()]
            current_languages = []

            codes = distinct(get_lang() or ['en'])

            # add primary languages
            for language in codes:
                language = sanitize_language_code(language)
                if language in available_languages:
                    current_languages.append(language_info(language))

            # fallback for browsers which only send languages like "en-US"
            if len(current_languages) == 0:
                for language in codes:
                    language = parse_locale(sanitize_language_code(language))[0]
                    if language in available_languages and language not in current_languages:
                        current_languages.append(language_info(language))

            return current_languages

        tmpl_context.available_languages = languages()

        tmpl_context.primary_languages = get_primary_languages()
        tmpl_context.secondary_languages = [lang for lang in tmpl_context.available_languages if lang not in tmpl_context.primary_languages]

        tmpl_context.current_language = tmpl_context.primary_languages[0]

        if request.identity is not None and \
           'user' in request.identity and \
           request.identity['user'] is None:
            raise redirect(url('/logout_handler',
                               params=dict(came_from=request.url.encode('utf-8'))))
