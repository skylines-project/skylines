# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, url, lurl, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from skylines import model
from skylines.model import DBSession
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController

from skylines.lib.base import BaseController
from skylines.controllers.error import ErrorController
from skylines.controllers.test import TestController
from skylines.controllers.flights import FlightsController
from skylines.controllers.upload import UploadController

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
    test = TestController()
    flights = FlightsController()
    upload = UploadController()

    @expose('skylines.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page = 'index')

    @expose('skylines.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page = 'about')

    @expose('skylines.templates.login')
    def login(self, came_from = lurl('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page = 'login', login_counter = str(login_counter),
                    came_from = came_from)

    @expose()
    def post_login(self, came_from = lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login',
                params = dict(came_from = came_from, __logins = login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from = lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
