# -*- coding: utf-8 -*-

from tg import expose, validate, redirect, require, request, config, flash
from tg.i18n import ugettext as _, lazy_ugettext as l_
import smtplib, email
from webob.exc import HTTPNotFound, HTTPForbidden
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from formencode import Schema, All
from formencode.validators import FieldsMatch, Email, String
from sprox.validators import UniqueValue
from sprox.saormprovider import SAORMProvider
from tw.forms import PasswordField, TextField, HiddenField
from tw.forms.validators import UnicodeString
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Group, Club, Flight, Follower
from skylines.model.igcfile import IGCFile
from skylines.form import BootstrapForm
from sqlalchemy.sql.expression import desc, and_, or_
from sqlalchemy import func
from repoze.what.predicates import not_anonymous, has_permission
from skylines.model.geo import Location

class ClubSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        clubs = DBSession.query(Club).order_by(Club.name).all()
        options = [(None, 'None')] + \
                  [(club.id, club.name) for club in clubs]
        d['options'] = options
        return d

class SelectClubForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __hide_fields__ = ['user_id']
    __limit_fields__ = ['club']
    club = ClubSelectField

select_club_form = SelectClubForm(DBSession)


class NewClubForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Club
    __limit_fields__ = ['name']
    name = TextField

new_club_form = NewClubForm(DBSession)

user_validator = Schema(chained_validators=(FieldsMatch('password',
                                                        'verify_password',
                                                        messages={'invalidNoMatch':
                                                                  'Passwords do not match'}),))


class NewUserForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __required_fields__ = ['password']
    __limit_fields__ = ['user_name', 'password', 'verify_password', 'email_address', 'display_name', 'club']
    __base_validator__ = user_validator
    user_name = TextField
    email_address = Field(TextField, All(UniqueValue(SAORMProvider(DBSession),
                                                     __model__, 'email_address'),
                                         Email(not_empty=True)))
    display_name = TextField(not_empty=True)
    club = ClubSelectField
    password = String(min=6)
    verify_password = PasswordField('verify_password')

new_user_form = NewUserForm(DBSession)


class EditUserForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __hide_fields__ = ['user_id']
    __limit_fields__ = ['user_name', 'email_address', 'display_name', 'club']
    __base_widget_args__ = dict(action='save')
    user_name = TextField
    email_address = Field(TextField, Email(not_empty=True))
    display_name = TextField(not_empty=True)
    club = ClubSelectField

edit_user_form = EditUserForm(DBSession)

recover_email_form = BootstrapForm('recover_email_form',
                                   submit_text="Recover Password",
                                   action='recover_email',
                                   children=[
    TextField('email_address', validator=Email(not_empty=True))
])

recover_password_form = BootstrapForm('recover_password_form',
                                      submit_text="Recover Password",
                                      action='recover_post',
                                      validator=user_validator,
                                      children=[
    HiddenField('key'),
    PasswordField('password', validator=UnicodeString(min=6)),
    PasswordField('verify_password'),
])

change_password_form = BootstrapForm('change_password_form',
                                     submit_text="Change Password",
                                     action='save_password',
                                     validator=user_validator,
                                     children=[
    PasswordField('password', validator=UnicodeString(min=6)),
    PasswordField('verify_password'),
])


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
    msg['Date'] = email.Utils.formatdate(localtime = 1)

    smtp = smtplib.SMTP(config.get('smtp_server', 'localhost'))
    smtp.ehlo()
    smtp.sendmail(config.get('email_from', 'skylines@xcsoar.org').encode('ascii'),
                  user.email_address.encode('ascii'), msg.as_string())
    smtp.quit()

class UserController(BaseController):
    def __init__(self, user):
        self.user = user

    @expose('skylines.templates.users.view')
    def index(self):
        return dict(page='settings', user=self.user,
                    distance_flights=self.get_distance_flights(),
                    takeoff_locations=self.get_takeoff_locations())

    @expose('skylines.templates.generic.form')
    def change_password(self, **kw):
        if not self.user.is_writable():
            raise HTTPForbidden

        return dict(page='settings', title=_('Change Password'),
                    form=change_password_form, values={})

    @expose()
    @validate(change_password_form, error_handler=change_password)
    def save_password(self, password, verify_password):
        self.user.password = password
        self.user.recover_key = None
        return redirect('.')

    @expose()
    @require(has_permission('manage'))
    def recover_password(self):
        recover_user_password(self.user)
        flash('A password recovery email was sent to that user.')
        redirect('.')

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
        if not club:
            club = None
        self.user.club_id = club
        DBSession.flush()

        redirect('.')

    @expose('skylines.templates.users.change_club')
    def change_club(self, **kwargs):
        if not self.user.is_writable():
            raise HTTPForbidden

        return dict(user=self.user,
                    select_form=select_club_form,
                    create_form=new_club_form)

    @expose()
    @validate(form=select_club_form, error_handler=change_club)
    def select_club(self, club, **kwargs):
        if not self.user.is_writable():
            raise HTTPForbidden

        self.user.club_id = club

        # assign the user's new club to all of his flights that have
        # no club yet
        flights = DBSession.query(Flight).outerjoin(IGCFile)
        flights = flights.filter(and_(Flight.club_id == None,
                                      or_(Flight.pilot_id == self.user.user_id,
                                          IGCFile.owner_id == self.user.user_id)))
        for flight in flights:
            flight.club_id = club

        DBSession.flush()

        redirect('.')

    @expose()
    @validate(form=new_club_form, error_handler=change_club)
    def create_club(self, name, **kw):
        if not self.user.is_writable():
            raise HTTPForbidden

        current_user = request.identity['user']

        club = Club(name=name)
        club.owner_id = current_user.user_id
        DBSession.add(club)

        self.user.club = club

        DBSession.flush()

        redirect('.')

    @expose()
    def tracking_register(self, came_from = '/tracking/info'):
        if not self.user.is_writable():
            raise HTTPForbidden

        self.user.generate_tracking_key()

        redirect(came_from)

    def get_distance_flight(self, distance):
        return DBSession.query(Flight) \
                        .filter(Flight.pilot == self.user) \
                        .filter(Flight.olc_classic_distance >= distance) \
                        .order_by(Flight.landing_time) \
                        .first()

    def get_distance_flights(self):
        distance_flights = []

        largest_flight = self.user.get_largest_flights().first()
        if largest_flight:
            distance_flights.append([largest_flight.olc_classic_distance / 1000,
                                     largest_flight])

        for distance in [50, 100, 300, 500, 700, 1000]:
            distance_flight = self.get_distance_flight(distance * 1000)
            distance_flights.append([distance, distance_flight])

        distance_flights.sort()
        return distance_flights

    def get_takeoff_locations(self):
        return Location.get_clustered_locations(Flight.takeoff_location_wkt,
                                                filter=(Flight.pilot == self.user))

    @expose()
    @require(not_anonymous())
    def follow(self):
        Follower.follow(request.identity['user'], self.user)
        redirect('.')

    @expose()
    @require(not_anonymous())
    def unfollow(self):
        Follower.unfollow(request.identity['user'], self.user)
        redirect('.')

class UsersController(BaseController):
    @expose('skylines.templates.users.list')
    def index(self):
        users = DBSession.query(User).order_by(User.display_name)
        return dict(page='settings', users=users)

    @expose()
    def lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        try:
            user = DBSession.query(User).get(int(id))
        except ValueError:
            raise HTTPNotFound

        if user is None:
            raise HTTPNotFound

        controller = UserController(user)
        return controller, remainder

    @expose('skylines.templates.users.new')
    def new(self, **kwargs):
        return dict(page='users', form=new_user_form)

    @expose()
    @validate(form=new_user_form, error_handler=new)
    def new_post(self, user_name, display_name, club, email_address, password, **kw):
        if not club:
            club = None

        user = User(user_name=user_name, display_name=display_name, club_id=club,
                    email_address=email_address, password=password)
        user.created_ip = request.remote_addr
        user.generate_tracking_key()
        DBSession.add(user)

        pilots = DBSession.query(Group).filter(Group.group_name == 'pilots').first()
        if pilots:
            pilots.users.append(user)

        redirect('/')

    @expose('skylines.templates.generic.form')
    def recover(self, key=None, **kwargs):
        if key is None:
            return dict(page='users', form=recover_email_form, values={})
        else:
            user = User.by_recover_key(int(key, 16))
            if user is None:
                    raise HTTPNotFound

            return dict(page='users', form=recover_password_form,
                        values=dict(key=key))

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
        user = User.by_recover_key(int(key, 16))
        if user is None:
                raise HTTPNotFound

        user.password = password
        user.recover_key = None

        flash(_('Password changed.'))
        return redirect('/')

    @expose()
    @require(has_permission('manage'))
    def generate_keys(self):
        """Hidden method that generates missing tracking keys."""

        for user in DBSession.query(User):
            if user.tracking_key is None:
                user.generate_tracking_key()

        DBSession.flush()

        return redirect('/users/')
