# -*- coding: utf-8 -*-
"""Functional test suite for the controllers of the application."""

from paste.deploy import loadapp
from tg import config
from zope.testbrowser.wsgi import Browser

from skylines.tests import setup_app, teardown_db
from skylines import model

__all__ = ['TestController']


def setup():
    # Setup the database
    setup_app()

    # Remove the current session
    # The TestController creates his own sessions
    model.DBSession.remove()


def teardown():
    # Remove the database again
    teardown_db()


class TestController(object):
    """
    Base functional test case for the controllers.
    """

    application_under_test = 'main'

    def setUp(self):
        """Method called by nose before running each test"""
        # Loading the application:
        wsgiapp = loadapp('config:test.ini#%s' % self.application_under_test,
                          relative_to=config.here)
        self.browser = Browser('http://localhost/', wsgi_app=wsgiapp)

    def tearDown(self):
        """Method called by nose after running each test"""
        # Cleaning up the session
        model.DBSession.remove()
