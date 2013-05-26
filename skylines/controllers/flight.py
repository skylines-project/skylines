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


class FlightController(BaseController):
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
