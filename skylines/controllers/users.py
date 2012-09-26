# -*- coding: utf-8 -*-

from tg import expose, validate, redirect, require, request, config, flash
from tg.i18n import ugettext as _, ungettext
import smtplib
import email
from webob.exc import HTTPNotFound, HTTPForbidden
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from formencode import Schema, All
from formencode.validators import FieldsMatch, Email, String, NotEmpty
from sprox.validators import UniqueValue
from sprox.sa.provider import SAORMProvider
from tw.forms import PasswordField, TextField, CheckBox, HiddenField
from tw.forms.validators import UnicodeString
from skylines.lib.base import BaseController
from skylines.lib.dbutil import get_requested_record
from skylines.lib import units
from skylines.model import DBSession, User, Group, Club, Flight, Follower
from skylines.model.igcfile import IGCFile
from skylines.form import BootstrapForm
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy import func
from repoze.what.predicates import not_anonymous, has_permission
from skylines.model.geo import Location
from datetime import date, timedelta
from skylines.model.notification import create_follower_notification


class ClubSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        query = DBSession.query(Club.id, Club.name).order_by(Club.name)
        options = [(None, 'None')] + query.all()
        d['options'] = options
        return d

    def validate(self, value, *args, **kw):
        if isinstance(value, Club):
            value = value.id
        return super(ClubSelectField, self).validate(value, *args, **kw)


class DelaySelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        options = [(0, _('None'))]
        for x in range(1, 10) + range(10, 30, 5) + range(30, 61, 15):
            options.append((x, ungettext(u'%u minute', u'%u minutes', x) % x))
        d['options'] = options
        return d

class UnitSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        d['options'] = list(enumerate(x[0] for x in self.unit_registry))
        return d

class DistanceUnitSelectField(UnitSelectField):
    unit_registry = units.distance_units

class SpeedUnitSelectField(UnitSelectField):
    unit_registry = units.speed_units

class LiftUnitSelectField(UnitSelectField):
    unit_registry = units.lift_units

class AltitudeUnitSelectField(UnitSelectField):
    unit_registry = units.altitude_units

class UnitPresetSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        d['options'] = list(enumerate(x[0] for x in units.unit_presets))
        return d

class SelectClubForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __hide_fields__ = ['id']
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
    __limit_fields__ = ['email_address', 'display_name', 'password', 'verify_password', 'club']
    __base_validator__ = user_validator
    email_address = Field(TextField, All(UniqueValue(SAORMProvider(DBSession),
                                                     __model__, 'email_address'),
                                         Email(not_empty=True)))
    display_name = Field(TextField, NotEmpty)
    club = ClubSelectField
    password = String(min=6)
    verify_password = PasswordField('verify_password')

new_user_form = NewUserForm(DBSession)


class EditUserForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __hide_fields__ = ['id']
    __limit_fields__ = ['email_address', 'display_name', 'club',
                        'tracking_delay', 'unit_preset',
                        'distance_unit', 'speed_unit',
                        'lift_unit', 'altitude_unit',
                        'eye_candy']
    __base_widget_args__ = dict(action='save')
    email_address = Field(TextField, Email(not_empty=True))
    display_name = Field(TextField, NotEmpty)
    club = ClubSelectField
    tracking_delay = DelaySelectField
    unit_preset = UnitPresetSelectField("unit_preset")
    distance_unit = DistanceUnitSelectField
    speed_unit = SpeedUnitSelectField
    lift_unit = LiftUnitSelectField
    altitude_unit = AltitudeUnitSelectField
    eye_candy = Field(CheckBox)

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
                    takeoff_locations=self.get_takeoff_locations(),
                    last_year_statistics=self.get_last_year_statistics())

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
                    values=self.user,
                    include_after='skylines.templates.users.after-edit-form')

    @expose()
    @validate(form=edit_user_form, error_handler=edit)
    def save(self, email_address, display_name, club,
             tracking_delay=0, unit_preset=1,
             distance_unit=1, speed_unit=1,
             lift_unit=0, altitude_unit=0,
             eye_candy=False, **kwargs):
        if not self.user.is_writable():
            raise HTTPForbidden

        self.user.email_address = email_address
        self.user.display_name = display_name
        if not club:
            club = None
        self.user.club_id = club
        self.user.tracking_delay = tracking_delay

        unit_preset = int(unit_preset)
        if unit_preset == 0:
            self.user.distance_unit = distance_unit
            self.user.speed_unit = speed_unit
            self.user.lift_unit = lift_unit
            self.user.altitude_unit = altitude_unit
        else:
            self.user.unit_preset = unit_preset

        self.user.eye_candy = eye_candy
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
                                      or_(Flight.pilot_id == self.user.id,
                                          IGCFile.owner_id == self.user.id)))
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
        club.owner_id = current_user.id
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
            distance_flights.append([largest_flight.olc_classic_distance,
                                     largest_flight])

        for distance in [50000, 100000, 300000, 500000, 700000, 1000000]:
            distance_flight = self.get_distance_flight(distance)
            if distance_flight is not None:
                distance_flights.append([distance, distance_flight])

        distance_flights.sort()
        return distance_flights

    def get_last_year_statistics(self):
        query = DBSession.query(func.count('*').label('flights'),
                                func.sum(Flight.olc_classic_distance).label('distance'),
                                func.sum(Flight.duration).label('duration')) \
                         .filter(Flight.pilot == self.user) \
                         .filter(Flight.date_local > (date.today() - timedelta(days=365))) \
                         .first()

        last_year_statistics = dict(flights = 0,
                                    distance = 0,
                                    duration = timedelta(0),
                                    speed = 0)

        if query and query.flights > 0:
            duration_seconds = query.duration.days * 24 * 3600 + query.duration.seconds

            if duration_seconds > 0:
                last_year_statistics['speed'] = float(query.distance) / duration_seconds

            last_year_statistics['flights'] = query.flights
            last_year_statistics['distance'] = query.distance
            last_year_statistics['duration'] = query.duration

        return last_year_statistics

    def get_takeoff_locations(self):
        return Location.get_clustered_locations(Flight.takeoff_location_wkt,
                                                filter=(Flight.pilot == self.user))

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
    @expose('skylines.templates.users.list')
    def index(self):
        users = DBSession.query(User).order_by(User.display_name)
        return dict(page='settings', users=users)

    @expose()
    def _lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        controller = UserController(get_requested_record(User, id))
        return controller, remainder

    @expose('skylines.templates.users.new')
    def new(self, **kwargs):
        return dict(page='users', form=new_user_form)

    @expose()
    @validate(form=new_user_form, error_handler=new)
    def new_post(self, display_name, club, email_address, password, **kw):
        if not club:
            club = None

        user = User(display_name=display_name, club_id=club,
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
