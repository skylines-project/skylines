# -*- coding: utf-8 -*-

from tg import expose, validate, redirect, require, request
from tg.i18n import ugettext as _, lazy_ugettext as l_
from webob.exc import HTTPNotFound, HTTPForbidden
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from formencode import Schema
from formencode.validators import FieldsMatch, Email, String
from tw.forms import PasswordField, TextField
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
    email_address = Field(TextField, Email(not_empty=True))
    display_name = TextField
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
    display_name = TextField
    club = ClubSelectField

edit_user_form = EditUserForm(DBSession)


class UserController(BaseController):
    def __init__(self, user):
        self.user = user

    @expose('skylines.templates.users.view')
    def index(self):
        return dict(page='settings', user=self.user,
                    distance_flights=self.get_distance_flights(),
                    takeoff_locations=self.get_takeoff_locations())

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

    def get_largest_flight(self):
        return Flight.get_largest().filter(Flight.pilot == self.user).first()

    def get_distance_flight(self, distance):
        return DBSession.query(Flight) \
                        .filter(Flight.pilot == self.user) \
                        .filter(Flight.olc_classic_distance >= distance) \
                        .order_by(Flight.landing_time) \
                        .first()

    def get_distance_flights(self):
        distance_flights = []

        largest_flight = self.get_largest_flight()
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

    @expose()
    @require(has_permission('manage'))
    def generate_keys(self):
        """Hidden method that generates missing tracking keys."""

        for user in DBSession.query(User):
            if user.tracking_key is None:
                user.generate_tracking_key()

        DBSession.flush()

        return redirect('/users/')
