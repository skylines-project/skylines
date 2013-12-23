# -*- coding: utf-8 -*-
"""Functional test suite for the controllers of the application."""

import pytest
from zope.testbrowser.wsgi import Browser


__all__ = ['TestController']


class TestController(object):
    """
    Base functional test case for the controllers.
    """

    @pytest.fixture(autouse=True)
    def setup_browser(self, frontend):
        self.browser = Browser('http://localhost/', wsgi_app=frontend.wsgi_app)
