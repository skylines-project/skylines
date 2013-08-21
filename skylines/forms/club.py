from flask import g
from flask.ext.babel import lazy_gettext as l_

from formencode.validators import URL
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from tw.forms import TextField

from .bootstrap import BootstrapForm
from skylines import db
from skylines.model import User, Club
from skylines.lib.validators import UniqueValueUnless


class SelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        query = db.session.query(Club.id, Club.name).order_by(Club.name)
        options = [(None, 'None')] + query.all()
        d['options'] = options
        return d

    def validate(self, value, *args, **kw):
        if isinstance(value, Club):
            value = value.id
        return super(SelectField, self).validate(value, *args, **kw)


class SelectForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __hide_fields__ = ['id']
    __limit_fields__ = ['club']
    __field_widget_args__ = {
        'club': dict(label_text=l_('Club'))
    }

    club = SelectField


select_form = SelectForm(db.session)


class NewForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Club
    __limit_fields__ = ['name']
    __field_widget_args__ = {
        'name': dict(label_text=l_('Name'))
    }

    name = TextField

new_form = NewForm(db.session)


def filter_club_id(model):
    return model.id == g.club_id


class EditForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Club
    __hide_fields__ = ['id']
    __limit_fields__ = ['name', 'website']
    __field_widget_args__ = {
        'name': dict(label_text=l_('Name')),
        'website': dict(label_text=l_('Website')),
    }

    name = Field(TextField, UniqueValueUnless(filter_club_id, db.session, __model__, 'name'))
    website = Field(TextField, URL())

edit_form = EditForm(db.session)
