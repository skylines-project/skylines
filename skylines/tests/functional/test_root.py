# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.
"""
from skylines.tests.functional import TestController


class TestRootController(TestController):
    """Tests for the method in the root controller."""

    def test_index(self):
        """The front page is redirecting properly"""
        self.browser.open('/')

        assert self.browser.url.endswith('/flights/today')
