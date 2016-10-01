from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from wtforms import PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email


class LoginForm(Form):
    email_address = EmailField(l_('Email Address'), validators=[
        InputRequired(message=l_('Please enter your email address.')),
        Email(),
    ])
    password = PasswordField(l_('Password'), validators=[
        InputRequired(message=l_('Please enter your password.')),
    ])
    remember_me = BooleanField(l_('Remember me'))
