from skylines.model import User


def test_global_register_link(browser):
    """User registration link is in the top bar"""

    # Check for link on start page
    link = browser.getLink(url='/users/new')
    assert link is not None, \
        'No registration link found on %s' % browser.url


def test_register_button(browser):
    """User registration link is in the login page"""

    # Check for link on login page
    browser.open('/login')
    link = browser.getLink(url='/users/new', index=1)
    assert link is not None, \
        'No registration link found on %s' % browser.url


def open_and_fill_register_form(browser, email, first_name, last_name, password,
                                verify_password=None):
    if verify_password is None:
        verify_password = password

    # Open user registration page
    browser.open('/users/new')

    # Find registration form
    form = browser.getForm(index=2)

    form.getControl(name='email_address').value = email
    form.getControl(name='first_name').value = first_name
    form.getControl(name='last_name').value = last_name
    form.getControl(name='password').value = password
    form.getControl(name='verify_password').value = verify_password

    return form


def register_user(browser, email, first_name, last_name,
                  password, verify_password=None):
    form = open_and_fill_register_form(
        browser, email, first_name, last_name, password,
        verify_password=verify_password
    )
    form.submit()

    user = User.by_email_address(email)
    assert user is not None, \
        "The user could not be found: %s" % email
    assert user.email_address == email
    assert user.first_name == first_name
    assert user.last_name == last_name


def expect_error(browser, response,
                 email=u'expect_error@skylines.aero',
                 first_name=u'Functional',
                 last_name=u'Test',
                 password=u'lambda',
                 verify_password=None,
                 check_user_exists=True):
    form = open_and_fill_register_form(
        browser, email, first_name, last_name, password,
        verify_password=verify_password
    )
    form.submit()

    if check_user_exists:
        user = User.by_email_address(email)
        assert user is None, \
            "The user has been created by mistake: %s" % email

    assert response in browser.contents, \
        "String not found in response: %s\n%s" % \
        (response, browser.contents)


def test_registration(browser):
    """User registration works properly"""

    first_name = u'Functional'
    last_name = u'Test'
    email = u'test_registration@skylines.aero'
    register_user(browser, email, first_name, last_name, password='lambda')


def test_validation_errors(browser):
    """Validation errors are working as expected"""

    expect_error(browser, 'Please enter your email address', email=u'')
    expect_error(browser, 'Invalid email address', email=u'abc')
    expect_error(browser, 'Invalid email address', email=u'abc@')
    expect_error(browser, 'Invalid email address', email=u'abc@de')
    expect_error(browser, 'Invalid email address', email=u'abc@de.')

    expect_error(browser, 'Please enter your first name', first_name=u'')
    expect_error(browser, 'Please enter your last name', last_name=u'')

    expect_error(browser, 'Your password must have at least 6 characters',
                 password=u'abc')
    expect_error(browser, 'Your passwords do not match',
                 password=u'lambda',
                 verify_password=u'lambda2')


def test_duplicates(browser):
    """Duplicate mail addresses are rejected"""
    email = u'test_duplicates@skylines.aero'
    first_name = u'Duplicate'
    last_name = u'Test'

    register_user(browser, email, first_name, last_name, 'lambda')
    expect_error(browser, 'A pilot with this email address exists already.',
                 email, first_name, last_name, u'lambda', check_user_exists=False)
