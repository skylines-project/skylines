# -*- coding: utf-8 -*-
"""Main Controller"""

from datetime import datetime
from tg import expose, flash, url, lurl, request, redirect, require, config
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import Any, not_anonymous
from skylines import model
from skylines.model import DBSession
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController

from skylines.lib.base import BaseController
from skylines.controllers.error import ErrorController
from skylines.controllers.users import UsersController
from skylines.controllers.clubs import ClubsController
from skylines.controllers.flights import FlightsController
from skylines.controllers.ranking import RankingController
from skylines.controllers.tracking import TrackingController
from skylines.controllers.static import StaticResourceController
from skylines.controllers.statistics import StatisticsController

import mapproxy.wsgiapp as mapproxy
from tg.controllers import WSGIAppController

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
    admin = AdminController(model, DBSession, config_type = TGAdminConfig)

    error = ErrorController()
    users = UsersController()
    clubs = ClubsController()
    flights = FlightsController()
    ranking = RankingController()
    tracking = TrackingController()
    static = StaticResourceController()
    statistics = StatisticsController()
    mapproxy = WSGIAppController(mapproxy.make_wsgi_app(config.get('skylines.mapproxy')))

    @expose()
    def index(self):
        """Handle the front-page."""
        redirect('/flights/today')

    @expose('skylines.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict()

    @expose('skylines.templates.login')
    def login(self, came_from = None):
        """Start the user login."""
        if not came_from:
            if request.referrer:
                came_from = request.referrer
            else:
                came_from = lurl('/')

        return dict(page = 'login', came_from = came_from)

    @expose()
    def post_login(self, came_from = None):
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
            flash(_('Sorry, username or password are wrong. Please try again or register.'), 'warning')
        else:
            request.identity['user'].login_ip = request.remote_addr
            request.identity['user'].login_time = datetime.now()

            flash(_('You are now logged in. Welcome back, %s!') % request.identity['user'])

        redirect(came_from)

    @expose()
    def post_logout(self, came_from = None):
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
    def settings(self):
        """Only for compatibility with old bookmarks."""
        redirect('/users/' + str(request.identity['user'].user_id))
