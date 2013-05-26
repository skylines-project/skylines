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


recover_email_form = BootstrapForm(
    'recover_email_form',
    submit_text=l_("Recover Password"),
    action='recover_email',
    children=[
        TextField('email_address',
                  validator=Email(not_empty=True),
                  label_text=l_('eMail Address'))
    ]
)

recover_password_form = BootstrapForm(
    'recover_password_form',
    submit_text=l_("Recover Password"),
    action='recover_post',
    validator=user_validator,
    children=[
        HiddenField('key'),
        PasswordField('password',
                      validator=UnicodeString(min=6),
                      label_text=l_('Password')),
        PasswordField('verify_password',
                      label_text=l_('Verify Password')),
    ]
)



def recover_user_password(user):
    key = user.generate_recover_key(request.remote_addr)

    text = u"""Hi %s,

you have asked to recover your password (from IP %s).  To enter a new
password, click on the following link:

 http://skylines.xcsoar.org/users/recover?key=%x

The SkyLines Team
""" % (unicode(user), request.remote_addr, key)

    msg = email.mime.text.MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = 'SkyLines password recovery'
    msg['From'] = config.get('email_from', 'skylines@xcsoar.org')
    msg['To'] = user.email_address.encode('ascii')
    msg['Date'] = email.Utils.formatdate(localtime=1)

    try:
        smtp = smtplib.SMTP(config.get('smtp_server', 'localhost'))
        smtp.ehlo()
        smtp.sendmail(config.get('email_from', 'skylines@xcsoar.org').encode('ascii'),
                      user.email_address.encode('ascii'), msg.as_string())
        smtp.quit()
    except:
        raise HTTPServiceUnavailable(explanation=_(
            "The mail server is currently not reachable. "
            "Please try again later or contact the developers."))


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

    @expose()
    @require(not_anonymous())
    def follow(self):
        Follower.follow(request.identity['user'], self.user)
        create_follower_notification(self.user, request.identity['user'])
        redirect('.')

    @expose()
    @require(not_anonymous())
    def unfollow(self):
        Follower.unfollow(request.identity['user'], self.user)
        redirect('.')


class UsersController(BaseController):
    @expose('generic/form.jinja')
    def recover(self, key=None, **kwargs):
        try:
            key = int(key, 16)
        except:
            key = None

        if key is None:
            return dict(active_page='users', form=recover_email_form, values={})
        else:
            user = User.by_recover_key(key)
            if user is None:
                    raise HTTPNotFound

            return dict(active_page='users', form=recover_password_form,
                        values=dict(key='%x' % key))

    @expose()
    @validate(form=recover_email_form, error_handler=recover)
    def recover_email(self, email_address, **kw):
        user = User.by_email_address(email_address)
        if user is None:
            raise HTTPNotFound

        recover_user_password(user)

        flash('Check your email, we have sent you a link to recover your password.')
        redirect('/')

    @expose()
    @validate(form=recover_password_form, error_handler=recover)
    def recover_post(self, key, password, verify_password, **kw):
        try:
            key = int(key, 16)
        except:
            key = None

        user = User.by_recover_key(key)
        if user is None:
                raise HTTPNotFound

        user.password = password
        user.recover_key = None

        flash(_('Password changed.'))
        return redirect('/')
