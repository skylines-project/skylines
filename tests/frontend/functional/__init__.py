# -*- coding: utf-8 -*-
"""Functional test suite for the controllers of the application."""

from zope.testbrowser.wsgi import Browser

import config
from tests import AppTest
from skylines import create_frontend_app

__all__ = ['TestController']


class TestController(AppTest):

    SETUP_DIRS = True
    BOOTSTRAP_DB = True

    def create_app(self):
        return create_frontend_app(config_file=config.TESTING_CONF_PATH)

    def setup(self):
        super(TestController, self).setup()
        self.browser = Browser('http://localhost/', wsgi_app=self.app.wsgi_app)
