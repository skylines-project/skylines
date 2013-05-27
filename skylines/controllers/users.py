# -*- coding: utf-8 -*-

import email
import smtplib
from datetime import date, timedelta

from tg import expose, validate, redirect, require, request, config, flash, cache
from tg.i18n import ugettext as _, ungettext, lazy_ugettext as l_
from webob.exc import HTTPNotFound, HTTPForbidden, HTTPServiceUnavailable
from tg.predicates import not_anonymous, has_permission

from formencode import Schema, All
from formencode.validators import FieldsMatch, Email, String, NotEmpty
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from sprox.validators import UniqueValue
from sprox.sa.provider import SAORMProvider
from tw.forms import PasswordField, TextField, CheckBox, HiddenField
from tw.forms.validators import UnicodeString

from sqlalchemy.sql.expression import and_, or_
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from .base import BaseController
from skylines.forms import BootstrapForm, units, club
from skylines.lib.validators import UniqueValueUnless
from skylines.lib.dbutil import get_requested_record
from skylines.model import (
    DBSession, User, Group, Club, Flight, Follower, Location, IGCFile
)
from skylines.model.notification import create_follower_notification


password_match_validator = FieldsMatch(
    'password', 'verify_password',
    messages={'invalidNoMatch': l_('Passwords do not match')})

user_validator = Schema(chained_validators=(password_match_validator,))


class NewUserForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __required_fields__ = ['password']
    __limit_fields__ = ['email_address', 'name', 'password', 'verify_password', 'club']
    __base_validator__ = user_validator
    __field_widget_args__ = {
        'email_address': dict(label_text=l_('eMail Address')),
        'name': dict(label_text=l_('Name')),
        'club': dict(label_text=l_('Club')),
        'password': dict(label_text=l_('Password')),
    }

    email_address = Field(TextField, All(UniqueValue(SAORMProvider(DBSession),
                                                     __model__, 'email_address'),
                                         Email(not_empty=True)))
    name = Field(TextField, NotEmpty)
    club = club.SelectField
    password = String(min=6)
    verify_password = PasswordField('verify_password',
                                    label_text=l_('Verify Password'))

new_user_form = NewUserForm(DBSession)


class UserController(BaseController):
    def __init__(self, user):
        self.user = user
        request.environ['UserController.user.id'] = self.user.id

    @expose()
    @require(has_permission('manage'))
    def recover_password(self):
        recover_user_password(self.user)
        flash('A password recovery email was sent to that user.')
        redirect('.')

    @expose('users/change_club.jinja')
    def change_club(self, **kwargs):
        if not self.user.is_writable(request.identity):
            raise HTTPForbidden

        return dict(user=self.user,
                    select_form=club.select_form,
                    create_form=club.new_form)

    @expose()
    @validate(form=club.select_form, error_handler=change_club)
    def select_club(self, club, **kwargs):
        if not self.user.is_writable(request.identity):
            raise HTTPForbidden

        self.user.club_id = club

        # assign the user's new club to all of his flights that have
        # no club yet
        flights = Flight.query().join(IGCFile)
        flights = flights.filter(and_(Flight.club_id == None,
                                      or_(Flight.pilot_id == self.user.id,
                                          IGCFile.owner_id == self.user.id)))
        for flight in flights:
            flight.club_id = club

        DBSession.flush()

        redirect('.')

    @expose()
    @validate(form=club.new_form, error_handler=change_club)
    def create_club(self, name, **kw):
        if not self.user.is_writable(request.identity):
            raise HTTPForbidden

        current_user = request.identity['user']

        club = Club(name=name)
        club.owner_id = current_user.id
        DBSession.add(club)

        self.user.club = club

        DBSession.flush()

        redirect('.')

    @expose()
    def tracking_register(self, came_from='/tracking/info'):
        if not self.user.is_writable(request.identity):
            raise HTTPForbidden

        self.user.generate_tracking_key()

        redirect(came_from)
