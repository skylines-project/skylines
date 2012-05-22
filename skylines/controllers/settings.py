# -*- coding: utf-8 -*-

from tg import expose, validate, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import not_anonymous
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from tw.forms import TextField
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Club

class ClubSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        clubs = DBSession.query(Club).all()
        options = [(None, 'None')] + \
                  [(club.id, club.name) for club in clubs]
        d['options'] = options
        return d

class SelectClubForm(EditableForm):
    __model__ = User
    __hide_fields__ = ['user_id']
    __limit_fields__ = ['club']
    club = ClubSelectField

select_club_form = SelectClubForm(DBSession)

class NewClubForm(AddRecordForm):
    __model__ = Club
    __limit_fields__ = ['name']
    name = TextField

new_club_form = NewClubForm(DBSession)

class SettingsController(BaseController):
    allow_only = not_anonymous()

    @expose('skylines.templates.settings.index')
    def index(self):
        user = User.by_user_name(request.identity['repoze.who.userid'])
        return dict(page='settings', user=user)

    @expose('skylines.templates.settings.change_club')
    def change_club(self, **kwargs):
        user = User.by_user_name(request.identity['repoze.who.userid'])
        return dict(page='settings', user=user,
                    select_form=select_club_form,
                    create_form=new_club_form)

    @expose()
    @validate(form=select_club_form, error_handler=change_club)
    def select_club(self, club, **kwargs):
        user = User.by_user_name(request.identity['repoze.who.userid'])
        user.club_id = club

        DBSession.flush()

        redirect('.')

    @expose()
    @validate(form=new_club_form, error_handler=change_club)
    def create_club(self, name, **kw):
        club = Club(name=name)
        DBSession.add(club)

        user = User.by_user_name(request.identity['repoze.who.userid'])
        user.club = club

        DBSession.flush()

        redirect('.')
