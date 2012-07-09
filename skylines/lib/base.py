# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context, request, redirect, url

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

    def __before__(self, *args, **kw):
        if request.identity is not None and \
           'user' in request.identity and \
           request.identity['user'] is None:
            raise redirect(url('/logout_handler',
                               params=dict(came_from=request.url.encode('utf-8'))))
