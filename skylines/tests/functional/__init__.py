# -*- coding: utf-8 -*-
"""Functional test suite for the controllers of the application."""

from zope.testbrowser.wsgi import Browser

from skylines.tests import setup_app, teardown_db, clean_db_and_bootstrap
from skylines import app, model

__all__ = ['TestController']


def setup():
    # Setup the Flask app
    app.add_web_components()

    # Setup the database
    setup_app()


def teardown():
    # Remove the database again
    teardown_db()


class TestController(object):
    """
    Base functional test case for the controllers.
    """

    def setUp(self):
        """Method called by nose before running each test"""
        clean_db_and_bootstrap()

        self.browser = Browser('http://localhost/', wsgi_app=app.wsgi_app)
