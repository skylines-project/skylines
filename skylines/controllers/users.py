# -*- coding: utf-8 -*-

from tg import expose, validate, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from webob.exc import HTTPNotFound, HTTPForbidden
from sprox.formbase import AddRecordForm, EditableForm, Field
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

class EditUserForm(EditableForm):
    __model__ = User
    __hide_fields__ = ['user_id']
    __limit_fields__ = ['user_name', 'email_address', 'display_name', 'club']
    __base_widget_args__ = dict(action='save')
    user_name = TextField
    email_address = Field(TextField, Email(not_empty=True))
    display_name = TextField
    club = ClubSelectField

edit_user_form = EditUserForm(DBSession)

class UserController(BaseController):
    def __init__(self, user):
        self.user = user

    @expose('skylines.templates.users.view')
    def index(self):
        return dict(page='settings', user=self.user)

    @expose('skylines.templates.generic.form')
    def edit(self, **kwargs):
        if not self.user.is_writable():
            raise HTTPForbidden

        return dict(page='settings', title=_('Edit User'),
                    form=edit_user_form,
                    values=self.user)

    @expose()
    @validate(form=edit_user_form, error_handler=edit)
    def save(self, user_name, email_address, display_name, club, **kwargs):
        if not self.user.is_writable():
            raise HTTPForbidden

        self.user.user_name = user_name
        self.user.email_address = email_address
        self.user.display_name = display_name
        if not club: club = None
        self.user.club_id = club
        DBSession.flush()

        redirect('.')

class UserIdController(BaseController):
    @expose()
    def lookup(self, id, *remainder):
        user = DBSession.query(User).get(int(id))
        if user is None:
            raise HTTPNotFound

        controller = UserController(user)
        return controller, remainder

class UsersController(BaseController):
    @expose('skylines.templates.users.list')
    def index(self):
        users = DBSession.query(User).order_by(User.display_name)
        return dict(page='settings', users=users)

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

    id = UserIdController()
