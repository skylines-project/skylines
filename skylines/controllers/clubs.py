# -*- coding: utf-8 -*-

from tg import expose, validate, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from webob.exc import HTTPNotFound, HTTPForbidden
from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.fillerbase import TableFiller
from tw.forms import TextField
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Group, Club

class EditClubForm(EditableForm):
    __model__ = Club
    __hide_fields__ = ['id']
    __limit_fields__ = ['name']
    __base_widget_args__ = dict(action='save')
    name = TextField

edit_club_form = EditClubForm(DBSession)

class PilotsTable(TableBase):
    __model__ = User
    __limit_fields__ = ['display_name']
    __omit_fields__ = ['__actions__']

class PilotsTableFiller(TableFiller):
    __model__ = User

    def _do_get_provider_count_and_objs(self, club, **kw):
        pilots = club.members
        return len(pilots), pilots

pilots_table = PilotsTable(DBSession)
pilots_filler = PilotsTableFiller(DBSession)

class NewPilotForm(AddRecordForm):
    __model__ = User
    __required_fields__ = ['display_name']
    __limit_fields__ = ['display_name']
    __base_widget_args__ = dict(action='create_pilot')
    display_name = TextField

new_pilot_form = NewPilotForm(DBSession)

class ClubController(BaseController):
    def __init__(self, club):
        self.club = club

    @expose('skylines.templates.clubs.view')
    def index(self):
        return dict(page='settings', club=self.club)

    @expose('skylines.templates.generic.form')
    def edit(self, **kwargs):
        if not self.club.is_writable():
            raise HTTPForbidden

        return dict(page='settings', title=_('Edit Club'),
                    form=edit_club_form,
                    values=self.club)

    @expose()
    @validate(form=edit_club_form, error_handler=edit)
    def save(self, name, **kwargs):
        if not self.club.is_writable():
            raise HTTPForbidden

        self.club.name = name
        DBSession.flush()

        redirect('.')

    @expose('skylines.templates.clubs.pilots')
    def pilots(self):
        return dict(page='settings', club=self.club, table=pilots_table, value=pilots_filler.get_value(club=self.club))

    @expose('skylines.templates.generic.form')
    def new_pilot(self, **kwargs):
        if not self.club.is_writable():
            raise HTTPForbidden

        return dict(page='settings', title=_("Create Pilot"),
                    form=new_pilot_form, values={})

    @expose()
    @validate(form=new_pilot_form, error_handler=new_pilot)
    def create_pilot(self, display_name, **kw):
        if not self.club.is_writable():
            raise HTTPForbidden

        pilot = User(user_name=display_name, display_name=display_name,
                     club=self.club)
        DBSession.add(pilot)

        pilots = DBSession.query(Group).filter(Group.group_name=='pilots').first()
        if pilots:
            pilots.users.append(pilot)

        redirect('pilots')

class ClubIdController(BaseController):
    @expose()
    def lookup(self, id, *remainder):
        club = DBSession.query(Club).get(int(id))
        if club is None:
            raise HTTPNotFound

        controller = ClubController(club)
        return controller, remainder

class ClubsController(BaseController):
    @expose('skylines.templates.clubs.list')
    def index(self):
        clubs = DBSession.query(Club).order_by(Club.name)
        return dict(page='settings', clubs=clubs)

    id = ClubIdController()
