# -*- coding: utf-8 -*-


def test_index(browser):
    """ The front page is show the about page """
    browser.open('/')

    assert 'Welcome to SkyLines' in browser.contents
