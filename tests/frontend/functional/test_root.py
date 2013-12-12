# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.
"""
from . import TestController


class TestRootController(TestController):
    """Tests for the method in the root controller."""

    def test_index(self):
        """ The front page is show the about page """
        self.browser.open('/')

        assert 'Welcome to SkyLines' in self.browser.contents
