# -*- coding: utf-8 -*-

from tg import expose, validate, request, redirect
from repoze.what.predicates import not_anonymous
from sqlalchemy.sql.expression import and_, or_
from sprox.formbase import AddRecordForm, EditableForm
from tw.forms import TextField
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Club, Flight
from skylines.controllers.users import ClubSelectField
from skylines.model.igcfile import IGCFile
from skylines.form import BootstrapForm

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


class SettingsController(BaseController):
    allow_only = not_anonymous()

    @expose('skylines.templates.settings.index')
    def index(self):
        user = request.identity['user']
        return dict(user=user)

    @expose('skylines.templates.settings.change_club')
    def change_club(self, **kwargs):
        user = request.identity['user']
        return dict(user=user,
                    select_form=select_club_form,
                    create_form=new_club_form)

    @expose()
    @validate(form=select_club_form, error_handler=change_club)
    def select_club(self, club, **kwargs):
        user = request.identity['user']
        user.club_id = club

        # assign the user's new club to all of his flights that have
        # no club yet
        flights = DBSession.query(Flight).outerjoin(IGCFile)
        flights = flights.filter(and_(Flight.club_id == None,
                                      or_(Flight.pilot_id == user.user_id,
                                          IGCFile.owner_id == user.user_id)))
        for flight in flights:
            flight.club_id = club

        DBSession.flush()

        redirect('.')

    @expose()
    @validate(form=new_club_form, error_handler=change_club)
    def create_club(self, name, **kw):
        user = request.identity['user']

        club = Club(name=name)
        club.owner_id = user.user_id
        DBSession.add(club)

        user.club = club

        DBSession.flush()

        redirect('.')

    @expose()
    def tracking_register(self, came_from = '/tracking/info'):
        user = request.identity['user']
        user.generate_tracking_key()

        redirect(came_from)
