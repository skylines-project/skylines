# -*- coding: utf-8 -*-

from tg import expose, validate, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from sprox.formbase import AddRecordForm, Field
from sprox.widgets import PropertySingleSelectField
from formencode import Schema
from formencode.validators import FieldsMatch, Email, String
from tw.forms import PasswordField, TextField
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Group, Club

class ClubSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        clubs = DBSession.query(Club).order_by(Club.name).all()
        options = [(None, 'None')] + \
                  [(club.id, club.name) for club in clubs]
        d['options'] = options
        return d

user_validator = Schema(chained_validators=(FieldsMatch('password',
                                                        'verify_password',
                                                        messages={'invalidNoMatch':
                                                                  'Passwords do not match'}),))

class NewUserForm(AddRecordForm):
    __model__ = User
    __required_fields__ = ['password']
    __limit_fields__ = ['user_name', 'password', 'verify_password', 'email_address', 'display_name', 'club']
    __base_validator__ = user_validator
    user_name = TextField
    email_address = Field(TextField, Email(not_empty=True))
    display_name = TextField
    club_id = ClubSelectField
    password = String(min=6)
    verify_password = PasswordField('verify_password')

new_user_form = NewUserForm(DBSession)

class UsersController(BaseController):
    @expose('skylines.templates.users.new')
    def new(self, **kwargs):
        return dict(page='users', form=new_user_form)

    @expose()
    @validate(form=new_user_form, error_handler=new)
    def new_post(self, user_name, display_name, club, email_address, password, **kw):
        if not club: club = None
        user = User(user_name=user_name, display_name=display_name, club_id=club,
                    email_address=email_address, password=password)
        DBSession.add(user)

        pilots = DBSession.query(Group).filter(Group.group_name=='pilots').first()
        if pilots:
            pilots.users.append(user)

        redirect('/')
