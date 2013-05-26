import math
import logging
from datetime import datetime

from tg import expose, validate, require, request, redirect, flash
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.decorators import with_trailing_slash, without_trailing_slash
from tg.predicates import has_permission
from webob.exc import HTTPBadRequest, HTTPNotFound, HTTPForbidden

from formencode.validators import String
from tw.forms.fields import TextField
from sprox.formbase import EditableForm
from sprox.widgets import PropertySingleSelectField

from sqlalchemy.sql.expression import func, and_, literal_column
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

from .base import BaseController
from skylines.forms import BootstrapForm, aircraft_model
from skylines.lib import files
from skylines.lib.xcsoar import analyse_flight, flight_path
from skylines.lib.helpers import format_time, format_number
from skylines.lib.formatter import units
from skylines.lib.datetime import from_seconds_of_day
from skylines.lib.geo import METERS_PER_DEGREE
from skylines.lib.sql import extract_array_item
from skylines.model import (
    DBSession, User, Flight, FlightPhase, Location, Elevation, FlightComment
)
from skylines.model.notification import create_flight_comment_notifications
from skylinespolyencode import SkyLinesPolyEncoder

log = logging.getLogger(__name__)


class PilotSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        query = DBSession.query(User.id, User.name) \
            .filter(User.club_id == request.identity['user'].club_id) \
            .order_by(User.name)
        options = [(None, 'None')] + query.all()
        d['options'] = options
        return d

    def validate(self, value, *args, **kw):
        if isinstance(value, User):
            value = value.id
        return super(PilotSelectField, self).validate(value, *args, **kw)


class SelectPilotForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Flight
    __hide_fields__ = ['id']
    __limit_fields__ = ['pilot', 'co_pilot']
    __base_widget_args__ = dict(action='select_pilot')
    pilot = PilotSelectField('pilot', label_text=l_('Pilot'))
    co_pilot = PilotSelectField('co_pilot', label_text=l_('Co-Pilot'))

select_pilot_form = SelectPilotForm(DBSession)


class SelectAircraftForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Flight
    __hide_fields__ = ['id']
    __limit_fields__ = ['model', 'registration', 'competition_id']
    __base_widget_args__ = dict(action='select_aircraft')
    model = aircraft_model.SelectField('model', label_text=l_('Aircraft Model'))
    registration = TextField('registration', label_text=l_('Aircraft Registration'), maxlength=32, validator=String(max=32))
    competition_id = TextField('competition_id', label_text=l_('Competition Number'), maxlength=5, validator=String(max=5))

select_aircraft_form = SelectAircraftForm(DBSession)


class FlightController(BaseController):
    @without_trailing_slash
    @expose('generic/form.jinja')
    def change_aircraft(self, **kwargs):
        if not self.flight.is_writable(request.identity):
            raise HTTPForbidden

        if self.flight.model_id is None:
            model_id = self.flight.igc_file.guess_model()
        else:
            model_id = self.flight.model_id

        if self.flight.registration is not None:
            registration = self.flight.registration
        elif self.flight.igc_file.registration is not None:
            registration = self.flight.igc_file.registration
        else:
            registration = self.flight.igc_file.guess_registration()

        if self.flight.competition_id is not None:
            competition_id = self.flight.competition_id
        elif self.flight.igc_file.competition_id is not None:
            competition_id = self.flight.igc_file.competition_id
        else:
            competition_id = None

        return dict(active_page='flights', title=_('Change Aircraft'),
                    form=select_aircraft_form,
                    values=dict(id=self.flight.id,
                                model=model_id,
                                registration=registration,
                                competition_id=competition_id))

    @without_trailing_slash
    @expose()
    @validate(form=select_aircraft_form, error_handler=change_aircraft)
    def select_aircraft(self, model, registration, competition_id, **kwargs):
        if not self.flight.is_writable(request.identity):
            raise HTTPForbidden

        if registration is not None:
            registration = registration.strip()
            if len(registration) == 0:
                registration = None

        self.flight.model_id = model
        self.flight.registration = registration
        self.flight.competition_id = competition_id
        self.flight.time_modified = datetime.utcnow()
        DBSession.flush()

        redirect('.')

    @without_trailing_slash
    @expose()
    @require(has_permission('upload'))
    def analysis(self, **kwargs):
        """Hidden method that restarts flight analysis."""

        analyse_flight(self.flight)
        DBSession.flush()

        return redirect('.')

    @without_trailing_slash
    @expose('generic/confirm.jinja')
    def delete(self, **kwargs):
        if not self.flight.is_writable(request.identity):
            raise HTTPForbidden

        if request.method == 'POST':
            files.delete_file(self.flight.igc_file.filename)
            DBSession.delete(self.flight)
            DBSession.delete(self.flight.igc_file)

            redirect('/flights/')
        else:
            return dict(title=_('Delete Flight'),
                        question=_('Are you sure you want to delete this flight?'),
                        action='delete', cancel='.')

    @without_trailing_slash
    @expose()
    def add_comment(self, text, **kwargs):
        if request.identity is None:
            flash(_('You have to be logged in to post comments!'), 'warning')
        else:
            text = text.strip()
            if len(text) == 0:
                redirect('.')

            comment = FlightComment()
            comment.user = request.identity['user']
            comment.flight = self.flight
            comment.text = text

            create_flight_comment_notifications(comment)

        redirect('.')
