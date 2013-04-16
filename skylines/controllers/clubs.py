# -*- coding: utf-8 -*-

from tg import expose, validate, redirect, request
from tg.i18n import ugettext as _
from tg.decorators import with_trailing_slash
from webob.exc import HTTPForbidden
from sqlalchemy import func

from .base import BaseController
from skylines.forms import club, pilot as pilot_forms
from skylines.lib.dbutil import get_requested_record
from skylines.model import DBSession, User, Group, Club


class ClubController(BaseController):
    def __init__(self, club):
        self.club = club

    @with_trailing_slash
    @expose('clubs/view.jinja')
    def index(self):
        return dict(active_page='settings', club=self.club)

    @expose('generic/form.jinja')
    def edit(self, **kwargs):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        return dict(active_page='settings', title=_('Edit Club'),
                    form=club.edit_form,
                    values=self.club)

    @expose()
    @validate(form=club.edit_form, error_handler=edit)
    def save(self, name, website, **kwargs):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        self.club.name = name
        self.club.website = website
        DBSession.flush()

        redirect('.')

    @expose('clubs/pilots.jinja')
    def pilots(self):
        return dict(active_page='settings', club=self.club, users=self.club.members)

    @expose('generic/form.jinja')
    def new_pilot(self, **kwargs):
        if not self.club.is_writable(request.identity):
            raise HTTPForbidden

        return dict(active_page='settings', title=_("Create Pilot"),
                    form=pilot_forms.new_form, values={})

    @expose()
    @validate(form=pilot_forms.new_form, error_handler=new_pilot)
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
    @expose('clubs/list.jinja')
    def index(self):
        clubs = DBSession.query(Club).order_by(func.lower(Club.name))
        return dict(active_page='settings', clubs=clubs)

    @expose()
    def _lookup(self, id, *remainder):
        controller = ClubController(get_requested_record(Club, id))
        return controller, remainder
