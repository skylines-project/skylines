# -*- coding: utf-8 -*-


def login(browser, email, password):
    form = browser.getForm(index=2)
    form.getControl(name='email_address').value = email
    form.getControl(name='password').value = password
    form.submit()


def test_forced_login(browser, test_user):
    """Anonymous users are forced to login

    Test that anonymous users are automatically redirected to the login
    form when authorization is denied. Next, upon successful login they
    should be redirected to the initially requested page.

    """
    # Requesting a protected area
    browser.open('/flights/upload/')
    assert browser.url.startswith('http://localhost/login')
    assert '</i> Logout' not in browser.contents

    login(browser, test_user.email_address, test_user.original_password)

    # Being redirected to the initially requested page:
    assert '</i> Logout' in browser.contents
    assert browser.url.startswith('http://localhost/flights/upload/'), \
        browser.url


def test_voluntary_login(browser, test_user):
    """Voluntary logins must work correctly"""

    # Going to the login form voluntarily:
    browser.open('/login')
    assert '</i> Logout' not in browser.contents

    # Submitting the login form:
    login(browser, test_user.email_address, test_user.original_password)

    # Being redirected to the home page:
    assert '</i> Logout' in browser.contents


def test_logout(browser, test_admin):
    """Logouts must work correctly"""

    browser.open('/login')

    # Logging in voluntarily the quick way:
    login(browser, test_admin.email_address, test_admin.original_password)

    # Check if the login succeeded
    assert '</i> Logout' in browser.contents

    # Logging out:
    browser.open('/logout')

    # Finally, redirected to the home page:
    assert '</i> Logout' not in browser.contents
