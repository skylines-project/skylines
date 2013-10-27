# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.
"""
from tests.functional import TestController
from nose.tools import assert_in


class TestRootController(TestController):
    """Tests for the method in the root controller."""

    def test_index(self):
        """ The front page is show the about page """
        self.browser.open('/')

        assert_in('Welcome to SkyLines', self.browser.contents)
