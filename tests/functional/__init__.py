# -*- coding: utf-8 -*-
"""Functional test suite for the controllers of the application."""

from zope.testbrowser.wsgi import Browser

import config
from tests import setup_app, teardown_db, clean_db_and_bootstrap
from skylines import create_frontend_app, model

__all__ = ['TestController']


class TestController(object):
    """
    Base functional test case for the controllers.
    """

    @classmethod
    def setup_class(cls):
        cls.app = create_frontend_app(config.TESTING_CONF_PATH)

        # Setup the database
        with cls.app.app_context():
            setup_app(cls.app)

    @classmethod
    def teardown_class(cls):
        # Remove the database again
        with cls.app.app_context():
            teardown_db()

    def setUp(self):
        """Method called by nose before running each test"""
        self.context = self.app.app_context()
        self.context.push()

        clean_db_and_bootstrap()

        self.browser = Browser('http://localhost/', wsgi_app=self.app.wsgi_app)

    def tearDown(self):
        self.context.pop()
