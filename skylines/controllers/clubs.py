# -*- coding: utf-8 -*-

from tg import expose, redirect
from webob.exc import HTTPNotFound
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Club

class PilotsTable(TableBase):
    __model__ = User
    __limit_fields__ = ['display_name', 'email_address']
    __omit_fields__ = ['__actions__']

class PilotsTableFiller(TableFiller):
    __model__ = User

    def _do_get_provider_count_and_objs(self, club, **kw):
        pilots = club.members
        return len(pilots), pilots

pilots_table = PilotsTable(DBSession)
pilots_filler = PilotsTableFiller(DBSession)

class ClubController(BaseController):
    def __init__(self, club):
        self.club = club

    @expose('skylines.templates.clubs.view')
    def index(self):
        return dict(page='settings', club=self.club)

    @expose('skylines.templates.clubs.pilots')
    def pilots(self):
        return dict(page='settings', club=self.club, table=pilots_table, value=pilots_filler.get_value(club=self.club))

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
