# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context, request, redirect, url
from tg.i18n import get_lang
from skylines.config.i18n import languages, language_info

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
        def get_current_language():
            available_languages = [lang['language_code'] for lang in languages()]
            current_languages = get_lang()
            for language in current_languages:
                if language in available_languages:
                    return language_info(language)

        tmpl_context.available_languages = languages()
        tmpl_context.current_language = get_current_language()

        if request.identity is not None and \
           'user' in request.identity and \
           request.identity['user'] is None:
            raise redirect(url('/logout_handler',
                               params=dict(came_from=request.url.encode('utf-8'))))
