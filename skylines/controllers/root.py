# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, request, config
from webob.exc import HTTPNotFound

from .base import BaseController
from .error import ErrorController
from .tracking import TrackingController

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
    tracking = TrackingController()

    _mapproxy_config = config.get('skylines.mapproxy')
    if _mapproxy_config is not None:
        # plug local mapproxy/mapserver at /mapproxy/
        from tg.controllers import WSGIAppController
        import mapproxy.wsgiapp as mapproxy
        mapproxy = WSGIAppController(mapproxy.make_wsgi_app(_mapproxy_config))

    @expose()
    def track(self, **kw):
        """LiveTrack24 tracking API"""

        if request.path != '/track.php':
            return HTTPNotFound()

        return self.tracking.lt24.track(**kw)

    @expose()
    def client(self, **kw):
        """LiveTrack24 tracking API"""

        if request.path != '/client.php':
            return HTTPNotFound()

        return self.tracking.lt24.client(**kw)

    @expose()
    def _lookup(self, *remainder):
        """
        Workaround: The production does not dispatch /track.php to the track
        method, so we use the _lookup() method to dispatch it manually.
        """

        if request.path == '/track.php':
            return self, ['track']

        if request.path == '/client.php':
            return self, ['client']

        raise HTTPNotFound()
