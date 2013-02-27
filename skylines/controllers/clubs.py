# -*- coding: utf-8 -*-

from tg import expose, validate, redirect, request
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.decorators import with_trailing_slash
from webob.exc import HTTPForbidden
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.validators import UniqueValue
from sprox.sa.provider import SAORMProvider
from formencode import validators, All
from tw.forms import TextField
from skylines.controllers.base import BaseController
from skylines.lib.dbutil import get_requested_record
from skylines.model import DBSession, User, Group, Club
from skylines.lib.form import BootstrapForm


class EditClubForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Club
    __hide_fields__ = ['id']
    __limit_fields__ = ['name', 'website']
    __base_widget_args__ = dict(action='save')
    __field_widget_args__ = {
        'name': dict(label_text=l_('Name')),
        'website': dict(label_text=l_('Website')),
    }

    name = TextField
    website = Field(TextField, validators.URL())

edit_club_form = EditClubForm(DBSession)


class NewPilotForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __required_fields__ = ['email_address', 'display_name']
    __limit_fields__ = ['email_address', 'display_name']
    __base_widget_args__ = dict(action='create_pilot')
    __field_widget_args__ = {
        'email_address': dict(label_text=l_('eMail Address')),
        'display_name': dict(label_text=l_('Name')),
    }

    email_address = Field(TextField, All(UniqueValue(SAORMProvider(DBSession),
                                                     __model__, 'email_address'),
                                         validators.Email))
    display_name = Field(TextField, validators.NotEmpty)

new_pilot_form = NewPilotForm(DBSession)


class ClubController(BaseController):
    def __init__(self, club):
        self.club = club

    @with_trailing_slash
    @expose('jinja:clubs/view.jinja')
    def index(self):
        return dict(page='settings', club=self.club)

    @expose('generic/form.html')
    def edit(self, **kwargs):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        return dict(page='settings', title=_('Edit Club'),
                    form=edit_club_form,
                    values=self.club)

    @expose()
    @validate(form=edit_club_form, error_handler=edit)
    def save(self, name, website, **kwargs):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        self.club.name = name
        self.club.website = website
        DBSession.flush()

        redirect('.')

    @expose('clubs/pilots.html')
    def pilots(self):
        return dict(page='settings', club=self.club, users=self.club.members)

    @expose('generic/form.html')
    def new_pilot(self, **kwargs):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        return dict(page='settings', title=_("Create Pilot"),
                    form=new_pilot_form, values={})

    @expose()
    @validate(form=new_pilot_form, error_handler=new_pilot)
    def create_pilot(self, email_address, display_name, **kw):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        pilot = User(display_name=display_name,
                     email_address=email_address, club=self.club)
        DBSession.add(pilot)

        pilots = DBSession.query(Group).filter(Group.group_name == 'pilots').first()
        if pilots:
            pilots.users.append(pilot)

        redirect('pilots')


class ClubsController(BaseController):
    @expose('jinja:clubs/list.jinja')
    def index(self):
        clubs = DBSession.query(Club).order_by(Club.name)
        return dict(page='settings', clubs=clubs)

    @expose()
    def _lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        controller = ClubController(get_requested_record(Club, id))
        return controller, remainder
