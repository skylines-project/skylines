# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, request, config
from webob.exc import HTTPNotFound

from .base import BaseController
from .error import ErrorController

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the SkyLines application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    error = ErrorController()

    _mapproxy_config = config.get('skylines.mapproxy')
    if _mapproxy_config is not None:
        # plug local mapproxy/mapserver at /mapproxy/
        from tg.controllers import WSGIAppController
        import mapproxy.wsgiapp as mapproxy
        mapproxy = WSGIAppController(mapproxy.make_wsgi_app(_mapproxy_config))
