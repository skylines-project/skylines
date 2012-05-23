# -*- coding: utf-8 -*-

from datetime import datetime
from tg import expose, validate, require, request, redirect, config
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from webob.exc import HTTPNotFound
from sqlalchemy.sql.expression import desc, or_
from sprox.formbase import EditableForm
from sprox.widgets import PropertySingleSelectField
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import DBSession, User, Flight

class PilotSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        users = DBSession.query(User).filter(User.club_id == request.identity['user'].club_id)
        options = [(None, 'None')] + \
                  [(user.user_id, user) for user in users]
        d['options'] = options
        return d

class SelectPilotForm(EditableForm):
    __model__ = Flight
    __hide_fields__ = ['id']
    __limit_fields__ = ['pilot', 'co_pilot']
    pilot = PilotSelectField
    co_pilot = PilotSelectField

select_pilot_form = SelectPilotForm(DBSession)

class FlightController(BaseController):
    def __init__(self, flight):
        self.flight = flight

    @expose('skylines.templates.flights.view')
    def index(self):
        from skylines.lib.analysis import flight_path
        fixes = flight_path(self.flight)

        import cgpolyencode
        encoder = cgpolyencode.GPolyEncoder(num_levels=4)
        fixes = encoder.encode(fixes)

        return dict(page='flights', flight=self.flight,
                    writable=self.flight.is_writable(),
                    fixes=fixes)

    @expose('skylines.templates.flights.map')
    def map(self):
        from skylines.lib.analysis import flight_path
        fixes = flight_path(self.flight)

        import cgpolyencode
        encoder = cgpolyencode.GPolyEncoder(num_levels=4)
        fixes = encoder.encode(fixes)

        return dict(page='flights', fixes=fixes)

    @expose('skylines.templates.flights.change_pilot')
    def change_pilot(self):
        return dict(page='settings', flight=self.flight,
                    form=select_pilot_form)

    @expose()
    @validate(form=select_pilot_form, error_handler=change_pilot)
    def select_pilot(self, pilot, co_pilot, **kwargs):
        user = request.identity['user']
        if self.flight.owner_id == user.user_id:
            if self.flight.pilot_id != pilot:
                self.flight.pilot_id = pilot
                if pilot:
                    self.flight.club_id = DBSession.query(User).get(pilot).club_id
            self.flight.co_pilot_id = co_pilot
            self.flight.time_modified = datetime.now()
            DBSession.flush()

        redirect('.')

    @expose()
    @require(has_permission('upload'))
    def analysis(self):
        """Hidden method that restarts flight analysis."""

        from skylines.lib.analysis import analyse_flight
        analyse_flight(self.flight)
        DBSession.flush()

        return redirect('/flights/id/' + str(self.flight.id))

class FlightIdController(BaseController):
    @expose()
    def lookup(self, id, *remainder):
        flight = DBSession.query(Flight).get(int(id))
        if flight is None:
            raise HTTPNotFound

        controller = FlightController(flight)
        return controller, remainder

class FlightsController(BaseController):
    @expose('skylines.templates.flights.list')
    def index(self):
        flights = DBSession.query(Flight).order_by(desc(Flight.takeoff_time))
        flights = flights.limit(250)
        return dict(page='flights', flights=flights)

    @expose('skylines.templates.flights.list')
    def my(self):
        flights = DBSession.query(Flight).order_by(desc(Flight.takeoff_time))
        if request.identity is not None:
            flights = flights.filter(or_(Flight.pilot == request.identity['user'],
                                         Flight.co_pilot == request.identity['user']))
        flights = flights.limit(250)
        return dict(page='flights', flights=flights)

    @expose('skylines.templates.flights.list')
    def my_club(self):
        flights = DBSession.query(Flight).order_by(desc(Flight.takeoff_time))
        if request.identity is not None and request.identity['user'].club_id:
            flights = flights.filter(Flight.club_id == request.identity['user'].club_id)
        flights = flights.limit(250)
        return dict(page='flights', flights=flights)

    @expose('skylines.templates.flights.list')
    def unassigned(self):
        flights = DBSession.query(Flight).order_by(desc(Flight.takeoff_time))
        flights = flights.filter(Flight.pilot_id == None)
        if request.identity is not None:
            flights = flights.filter(Flight.owner == request.identity['user'])
        flights = flights.limit(250)
        return dict(page='flights', flights=flights)

    @expose('skylines.templates.flights.list')
    def pilot(self, id):
        flights = DBSession.query(Flight).filter(or_(Flight.pilot_id==id,
                                                     Flight.co_pilot_id==id))
        flights = flights.order_by(desc(Flight.takeoff_time))
        flights = flights.limit(250)
        return dict(page='flights', flights=flights)

    @expose('skylines.templates.flights.list')
    def club(self, id):
        flights = DBSession.query(Flight).filter(Flight.club_id==id)
        flights = flights.order_by(desc(Flight.takeoff_time))
        flights = flights.limit(250)
        return dict(page='flights', flights=flights)

    @expose()
    @require(has_permission('manage'))
    def analysis(self):
        """Hidden method that restarts flight analysis."""

        from skylines.lib.analysis import analyse_flight
        for flight in DBSession.query(Flight):
            analyse_flight(flight)
            DBSession.flush()

        return redirect('/flights/')

    id = FlightIdController()
