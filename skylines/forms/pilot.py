from flask import g
from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from formencode import validators, All
from sprox.formbase import AddRecordForm, Field
from sprox.validators import UniqueValue
from sprox.sa.provider import SAORMProvider
from tw.forms import SingleSelectField, TextField
from wtforms import SelectField as _SelectField, PasswordField
from wtforms.validators import Length, EqualTo

from .bootstrap import BootstrapForm
from skylines import db
from skylines.model import User


class NewForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __required_fields__ = ['email_address', 'name']
    __limit_fields__ = ['email_address', 'name']
    __base_widget_args__ = dict(action='create_pilot')
    __field_widget_args__ = {
        'email_address': dict(label_text=l_('eMail Address')),
        'name': dict(label_text=l_('Name')),
    }

    email_address = Field(TextField, All(
        UniqueValue(SAORMProvider(db.session), __model__, 'email_address'),
        validators.Email, validators.NotEmpty))

    name = Field(TextField, validators.NotEmpty)

new_form = NewForm(db.session)


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
