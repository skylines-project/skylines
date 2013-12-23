# -*- coding: utf-8 -*-

import pytest


@pytest.mark.usefixtures("app", "db", "bootstrap")
class TestAuthentication(object):
    """ Tests for the default authentication setup. """

    def login(self, browser, email, password):
        form = browser.getForm(index=2)
        form.getControl(name='email_address').value = email
        form.getControl(name='password').value = password
        form.submit()

    def test_forced_login(self, browser):
        """Anonymous users are forced to login

        Test that anonymous users are automatically redirected to the login
        form when authorization is denied. Next, upon successful login they
        should be redirected to the initially requested page.

        """
        # Requesting a protected area
        browser.open('/flights/upload/')
        assert browser.url.startswith('http://localhost/login')
        assert '</i> Logout' not in browser.contents

        self.login(browser, u'max+skylines@blarg.de', 'test')

        # Being redirected to the initially requested page:
        assert '</i> Logout' in browser.contents
        assert browser.url.startswith('http://localhost/flights/upload/'), \
            browser.url

    def test_voluntary_login(self, browser):
        """Voluntary logins must work correctly"""

        # Going to the login form voluntarily:
        browser.open('/login')
        assert '</i> Logout' not in browser.contents

        # Submitting the login form:
        self.login(browser, u'max+skylines@blarg.de', 'test')

        # Being redirected to the home page:
        assert '</i> Logout' in browser.contents

    def test_logout(self, browser):
        """Logouts must work correctly"""

        browser.open('/login')

        # Logging in voluntarily the quick way:
        self.login(browser, u'manager@somedomain.com', 'managepass')

        # Check if the login succeeded
        assert '</i> Logout' in browser.contents

        # Logging out:
        browser.open('/logout')

        # Finally, redirected to the home page:
        assert '</i> Logout' not in browser.contents
