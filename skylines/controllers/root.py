# -*- coding: utf-8 -*-
"""Main Controller"""

from datetime import datetime

from tg import expose, flash, lurl, request, redirect, require, config
from tg.i18n import ugettext as _, set_lang
from tg.predicates import Any, not_anonymous
from webob.exc import HTTPNotFound

from .base import BaseController
from .error import ErrorController
from .users import UsersController
from .clubs import ClubsController
from .flights import FlightsController
from .notifications import NotificationsController
from .ranking import RankingController
from .tracking import TrackingController
from .statistics import StatisticsController

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
    users = UsersController()
    clubs = ClubsController()
    flights = FlightsController()
    notifications = NotificationsController()
    ranking = RankingController()
    tracking = TrackingController()
    statistics = StatisticsController()

    _mapproxy_config = config.get('skylines.mapproxy')
    if _mapproxy_config is not None:
        # plug local mapproxy/mapserver at /mapproxy/
        from tg.controllers import WSGIAppController
        import mapproxy.wsgiapp as mapproxy
        mapproxy = WSGIAppController(mapproxy.make_wsgi_app(_mapproxy_config))

    @expose()
    def index(self, **kw):
        """Handle the front-page."""
        redirect('/flights/latest')

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
    def set_lang(self, language, **kw):
        set_lang(language)

        if request.referrer is None:
            redirect('/')
        else:
            redirect(request.referrer)

    @expose('login.jinja')
    def login(self, came_from=None, **kw):
        """Start the user login."""
        if not came_from:
            if request.referrer:
                came_from = request.referrer
            else:
                came_from = lurl('/')

        return dict(came_from=came_from)

    @expose()
    def post_login(self, came_from=None, **kw):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not came_from:
            if request.referrer:
                came_from = request.referrer
            else:
                came_from = lurl('/')

        if not request.identity:
            flash(_('Sorry, email address or password are wrong. Please try again or register.'), 'warning')
        else:
            request.identity['user'].login_ip = request.remote_addr
            request.identity['user'].login_time = datetime.utcnow()

            flash(_('You are now logged in. Welcome back, %s!') % request.identity['user'])

        redirect(came_from)

    @expose()
    def post_logout(self, came_from=None, **kw):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        if not came_from:
            if request.referrer:
                came_from = request.referrer
            else:
                came_from = lurl('/')

        flash(_('You are now logged out. We hope to see you back soon!'))
        redirect(came_from)

    @expose()
    @require(Any(not_anonymous(), msg='Please login to see this page!'))
    def settings(self, **kw):
        """Only for compatibility with old bookmarks."""
        redirect('/users/' + str(request.identity['user'].id))

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
