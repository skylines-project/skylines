# -*- coding: utf-8 -*-

from tg import expose, validate, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from webob.exc import HTTPNotFound, HTTPForbidden
from sprox.formbase import AddRecordForm, EditableForm, Field
from formencode import validators
from tw.forms import TextField
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Group, Club
from skylines.form import BootstrapForm

class EditClubForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Club
    __hide_fields__ = ['id']
    __limit_fields__ = ['name', 'website']
    __base_widget_args__ = dict(action='save')
    name = TextField
    website = Field(TextField, validators.URL())

edit_club_form = EditClubForm(DBSession)

class NewPilotForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
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
    def save(self, name, website, **kwargs):
        if not self.club.is_writable():
            raise HTTPForbidden

        self.club.name = name
        self.club.website = website
        DBSession.flush()

        redirect('.')

    @expose('skylines.templates.clubs.pilots')
    def pilots(self):
        users = DBSession.query(User).order_by(User.display_name)
        return dict(page='settings', club=self.club, users=self.club.members)

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


class ClubsController(BaseController):
    @expose('skylines.templates.clubs.list')
    def index(self):
        clubs = DBSession.query(Club).order_by(Club.name)
        return dict(page='settings', clubs=clubs)

    @expose()
    def lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        try:
            club = DBSession.query(Club).get(int(id))
        except ValueError:
            raise HTTPNotFound

        if club is None:
            raise HTTPNotFound

        controller = ClubController(club)
        return controller, remainder
