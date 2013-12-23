# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.
"""
import pytest


@pytest.mark.usefixtures("app")
class TestRootController(object):
    """Tests for the method in the root controller."""

    def test_index(self, browser):
        """ The front page is show the about page """
        browser.open('/')

        assert 'Welcome to SkyLines' in browser.contents
