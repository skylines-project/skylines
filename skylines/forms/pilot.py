from flask import g
from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from tw.forms import SingleSelectField
from wtforms import (
    TextField as _TextField, SelectField as _SelectField, PasswordField
)
from wtforms.validators import (
    Length, EqualTo, InputRequired, Email, ValidationError
)

from skylines.model import User


class SelectField(SingleSelectField):
    def update_params(self, d):
        users = User.query(club_id=g.current_user.club_id) \
            .order_by(User.name)

        options = [(None, '[unspecified]')] + \
                  [(user.id, user) for user in users]
        d['options'] = options

        return SingleSelectField.update_params(self, d)


class ClubPilotsSelectField(_SelectField):
    def __init__(self, *args, **kwargs):
        super(ClubPilotsSelectField, self).__init__(*args, **kwargs)
        self.coerce = int

    def process(self, *args, **kwargs):
        users = User.query(club_id=g.current_user.club_id).order_by(User.name)
        self.choices = [(0, '[unspecified]')]
        self.choices.extend([(user.id, user) for user in users])

        super(ClubPilotsSelectField, self).process(*args, **kwargs)


class ChangePasswordForm(Form):
    password = PasswordField(l_('Password'), validators=[
        Length(min=6),
    ])
    verify_password = PasswordField(l_('Verify Password'), validators=[
        EqualTo('password', message=l_('Passwords do not match')),
    ])


class CreatePilotForm(Form):
    email_address = _TextField(l_('eMail Address'), validators=[
        InputRequired(),
        Email(),
    ])
    name = _TextField(l_('Name'), validators=[
        InputRequired(),
    ])

    def validate_email_address(form, field):
        if User.exists(email_address=field.data):
            raise ValidationError(l_('A pilot with this email address exists already.'))
