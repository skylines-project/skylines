from tg import request
from tg.i18n import lazy_ugettext as l_

from formencode import validators, All
from sprox.formbase import AddRecordForm, Field
from sprox.validators import UniqueValue
from sprox.sa.provider import SAORMProvider
from tw.forms import SingleSelectField, TextField

from skylines.forms import BootstrapForm
from skylines.model import DBSession, User


class NewForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __required_fields__ = ['email_address', 'display_name']
    __limit_fields__ = ['email_address', 'display_name']
    __base_widget_args__ = dict(action='create_pilot')
    __field_widget_args__ = {
        'email_address': dict(label_text=l_('eMail Address')),
        'display_name': dict(label_text=l_('Name')),
    }

    email_address = Field(TextField, All(
        UniqueValue(SAORMProvider(DBSession), __model__, 'email_address'),
        validators.Email))

    display_name = Field(TextField, validators.NotEmpty)

new_form = NewForm(DBSession)


class SelectField(SingleSelectField):
    def update_params(self, d):
        users = DBSession.query(User) \
            .filter(User.club_id == request.identity['user'].club_id) \
            .order_by(User.display_name)

        options = [(None, '[unspecified]')] + \
                  [(user.id, user) for user in users]
        d['options'] = options

        return SingleSelectField.update_params(self, d)
