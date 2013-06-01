# -*- coding: utf-8 -*-
"""
Integration tests for the :mod:`repoze.who`-powered authentication sub-system.

As SkyLines grows and the authentication method changes, only these tests
should be updated.

"""

from skylines.tests.functional import TestController


class TestAuthentication(TestController):
    """Tests for the default authentication setup.

    By default in TurboGears 2, :mod:`repoze.who` is configured with the same
    plugins specified by repoze.what-quickstart (which are listed in
    http://code.gustavonarea.net/repoze.what-quickstart/#repoze.what.plugins.quickstart.setup_sql_auth).

    As the settings for those plugins change, or the plugins are replaced,
    these tests should be updated.

    """

    def test_forced_login(self):
        """Anonymous users are forced to login

        Test that anonymous users are automatically redirected to the login
        form when authorization is denied. Next, upon successful login they
        should be redirected to the initially requested page.

        """
        # Requesting a protected area
        self.browser.open('/flights/upload/')
        assert self.browser.url.startswith('http://localhost/login')

        # Getting the login form:
        form = self.browser.getForm(index=2)

        # Submitting the login form:
        form.getControl(name='login').value = u'max+skylines@blarg.de'
        form.getControl(name='password').value = 'test'
        form.submit()

        # Being redirected to the initially requested page:
        assert 'user_id=' in self.browser.cookies['session'], \
            'Session cookie was not defined: %s' % self.browser.cookies.items()
        assert self.browser.url.startswith('http://localhost/flights/upload/'), \
            self.browser.url

    def test_voluntary_login(self):
        """Voluntary logins must work correctly"""

        # Going to the login form voluntarily:
        self.browser.open('/login')
        form = self.browser.getForm(index=2)

        # Submitting the login form:
        form.getControl(name='login').value = u'max+skylines@blarg.de'
        form.getControl(name='password').value = 'test'
        form.submit()

        # Being redirected to the home page:
        assert 'user_id=' in self.browser.cookies['session'], \
            'Session cookie was not defined: %s' % self.browser.cookies.items()

    def test_logout(self):
        """Logouts must work correctly"""

        # Logging in voluntarily the quick way:
        self.browser.post('/login', 'login={login}&password={password}'
                          .format(login=u'manager@somedomain.com',
                                  password='managepass'))

        # Check if the login succeeded
        assert 'user_id=' in self.browser.cookies['session'], \
            'Session cookie was not defined: %s' % self.browser.cookies.items()

        print self.browser.cookies
        # Logging out:
        self.browser.open('/logout')
        print self.browser.cookies

        # Finally, redirected to the home page:
        authtkt = self.browser.cookies.get('session')
        assert 'user_id=' not in self.browser.cookies['session'], \
            'Session cookie was not deleted: %s' % self.browser.cookies.items()
