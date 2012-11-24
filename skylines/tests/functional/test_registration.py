from skylines.tests.functional import TestController
from skylines.model import User


class TestRegistration(TestController):
    def test_global_register_link(self):
        """User registration link is in the top bar"""

        # Check for link on start page
        link = self.browser.getLink(url='/users/new')
        assert link is not None, \
               'No registration link found on %s' % self.browser.url

    def test_register_button(self):
        """User registration link is in the login page"""

        # Check for link on login page
        self.browser.open('/login')
        link = self.browser.getLink(url='/users/new', index=1)
        assert link is not None, \
               'No registration link found on %s' % self.browser.url

    def open_and_fill_register_form(self, email, name, password):
        # Open user registration page
        self.browser.open('/users/new')

        # Find registration form
        form = self.browser.getForm(action='new_post')

        form.getControl(name='email_address').value = email
        form.getControl(name='display_name').value = name
        form.getControl(name='password').value = password
        form.getControl(name='verify_password').value = password

        return form

    def test_registration(self):
        """User registration works properly"""

        name = u'Functional Test'
        email = u'functional@test.de'

        form = self.open_and_fill_register_form(email, name, 'lambda')
        form.submit()

        user = User.by_email_address(email)
        assert user is not None, \
               "The user could not be found: %s" % email
        assert user.email_address == email
        assert user.display_name == name
