from flask import g
from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from wtforms import PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email

from skylines.model import User
from .select import GroupSelectField


class ClubPilotsSelectField(GroupSelectField):
    def __init__(self, *args, **kwargs):
        super(ClubPilotsSelectField, self).__init__(*args, **kwargs)
        self.coerce = int

    def process(self, *args, **kwargs):
        self.choices = [
            (0, '[' + l_('Unknown or other person') + ']'),
            (g.current_user.id, g.current_user.name),
        ]

        club = g.current_user.club
        if club:
            members = User.query(club_id=club.id) \
                .order_by(User.name) \
                .filter(User.id != g.current_user.id)

            members = [(member.id, member.name) for member in members]

            self.choices.append((club.name, members))

        super(ClubPilotsSelectField, self).process(*args, **kwargs)


class LoginForm(Form):
    email_address = EmailField(l_('Email Address'), validators=[
        InputRequired(message=l_('Please enter your email address.')),
        Email(),
    ])
    password = PasswordField(l_('Password'), validators=[
        InputRequired(message=l_('Please enter your password.')),
    ])
    remember_me = BooleanField(l_('Remember me'))
