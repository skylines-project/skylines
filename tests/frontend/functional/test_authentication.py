# -*- coding: utf-8 -*-

from . import TestController


class TestAuthentication(TestController):
    """ Tests for the default authentication setup. """

    def login(self, email, password):
        form = self.browser.getForm(index=2)
        form.getControl(name='email_address').value = email
        form.getControl(name='password').value = password
        form.submit()

    def test_forced_login(self):
        """Anonymous users are forced to login

        Test that anonymous users are automatically redirected to the login
        form when authorization is denied. Next, upon successful login they
        should be redirected to the initially requested page.

        """
        # Requesting a protected area
        self.browser.open('/flights/upload/')
        assert self.browser.url.startswith('http://localhost/login')
        assert '</i> Logout' not in self.browser.contents

        self.login(u'max+skylines@blarg.de', 'test')

        # Being redirected to the initially requested page:
        assert '</i> Logout' in self.browser.contents
        assert self.browser.url.startswith('http://localhost/flights/upload/'), \
            self.browser.url

    def test_voluntary_login(self):
        """Voluntary logins must work correctly"""

        # Going to the login form voluntarily:
        self.browser.open('/login')
        assert '</i> Logout' not in self.browser.contents

        # Submitting the login form:
        self.login(u'max+skylines@blarg.de', 'test')

        # Being redirected to the home page:
        assert '</i> Logout' in self.browser.contents

    def test_logout(self):
        """Logouts must work correctly"""

        self.browser.open('/login')

        # Logging in voluntarily the quick way:
        self.login(u'manager@somedomain.com', 'managepass')

        # Check if the login succeeded
        assert '</i> Logout' in self.browser.contents

        # Logging out:
        self.browser.open('/logout')

        # Finally, redirected to the home page:
        assert '</i> Logout' not in self.browser.contents
