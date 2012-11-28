from urllib2 import HTTPError

from skylines.tests.functional import TestController


class TestStaticMiddleware(TestController):

    def test_redirection(self):
        """Static Middleware redirects to the right file"""

        self.browser.mech_browser.set_handle_redirect(False)

        try:
            # Requesting a redirecting URL
            self.browser.open('/static/test/xyz.txt')

            raise AssertionError('HTTPError 301 expected, but browser.open() passed')
        except HTTPError, error:
            assert error.code == 302, \
                   'HTTPError.code is %d, expected 302' % error.code

            assert error.hdrs['location'] == 'http://localhost/does/not/exist/xyz.txt', \
                   'Static Middleware redirected to the wrong URL: %s' % error.hdrs['location']

    def test_unknown(self):
        """Static Middleware returns 404 if no redirection is found"""

        self.browser.mech_browser.set_handle_redirect(False)

        try:
            # Requesting a redirecting URL
            self.browser.open('/static/test234/xyz.txt')

            raise AssertionError('HTTPError 404 expected, but browser.open() passed')
        except HTTPError, error:
            assert error.code == 404, \
                   'HTTPError.code is %d, expected 404' % error.code
