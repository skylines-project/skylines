from datetime import date, timedelta

from flask import Blueprint, request, render_template, redirect, url_for, abort, g
from flask.ext.babel import lazy_gettext as l_, _

from formencode import Schema, All, Invalid
from formencode.validators import FieldsMatch, Email, String, NotEmpty
from sprox.formbase import AddRecordForm, EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from sprox.validators import UniqueValue
from sprox.sa.provider import SAORMProvider
from tw.forms import PasswordField, TextField, CheckBox, HiddenField
from tw.forms.validators import UnicodeString

from sqlalchemy.sql.expression import and_, or_
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from skylines.forms import BootstrapForm, units, club
from skylines.lib.validators import UniqueValueUnless
from skylines.lib.dbutil import get_requested_record
from skylines.model import (
    DBSession, User, Group, Club, Flight, Follower, Location, IGCFile
)
from skylines.model.notification import create_follower_notification

user_blueprint = Blueprint('user', 'skylines')


@user_blueprint.url_value_preprocessor
def _pull_user_id(endpoint, values):
    g.user_id = values.pop('user_id')
    g.user = get_requested_record(User, g.user_id)


@user_blueprint.url_defaults
def _add_user_id(endpoint, values):
    values.setdefault('user_id', g.user_id)


def _get_distance_flight(distance):
    return Flight.query() \
        .filter(Flight.pilot == g.user) \
        .filter(Flight.olc_classic_distance >= distance) \
        .order_by(Flight.landing_time) \
        .first()


def _get_distance_flights():
    distance_flights = []

    largest_flight = g.user.get_largest_flights().first()
    if largest_flight:
        distance_flights.append([largest_flight.olc_classic_distance,
                                 largest_flight])

    for distance in [50000, 100000, 300000, 500000, 700000, 1000000]:
        distance_flight = _get_distance_flight(distance)
        if distance_flight is not None:
            distance_flights.append([distance, distance_flight])

    distance_flights.sort()
    return distance_flights


def _get_last_year_statistics():
    query = DBSession.query(func.count('*').label('flights'),
                            func.sum(Flight.olc_classic_distance).label('distance'),
                            func.sum(Flight.duration).label('duration')) \
                     .filter(Flight.pilot == g.user) \
                     .filter(Flight.date_local > (date.today() - timedelta(days=365))) \
                     .first()

    last_year_statistics = dict(flights=0,
                                distance=0,
                                duration=timedelta(0),
                                speed=0)

    if query and query.flights > 0:
        duration_seconds = query.duration.days * 24 * 3600 + query.duration.seconds

        if duration_seconds > 0:
            last_year_statistics['speed'] = float(query.distance) / duration_seconds

        last_year_statistics['flights'] = query.flights
        last_year_statistics['distance'] = query.distance
        last_year_statistics['duration'] = query.duration

        last_year_statistics['average_distance'] = query.distance / query.flights
        last_year_statistics['average_duration'] = query.duration / query.flights

    return last_year_statistics


def _get_takeoff_locations():
    return Location.get_clustered_locations(Flight.takeoff_location_wkt,
                                            filter=(Flight.pilot == g.user))


@user_blueprint.route('/')
def index():
    return render_template(
        'users/view.jinja',
        active_page='settings', user=g.user,
        distance_flights=_get_distance_flights(),
        takeoff_locations=_get_takeoff_locations(),
        last_year_statistics=_get_last_year_statistics())


password_match_validator = FieldsMatch(
    'password', 'verify_password',
    messages={'invalidNoMatch': l_('Passwords do not match')})

change_password_form = BootstrapForm(
    'change_password_form',
    submit_text=l_("Change Password"),
    validator=Schema(chained_validators=(password_match_validator,)),
    children=[
        PasswordField('password',
                      validator=UnicodeString(min=6),
                      label_text=l_('Password')),
        PasswordField('verify_password',
                      label_text=l_('Verify Password')),
    ]
)


def change_password_post():
    try:
        change_password_form.validate(request.form)
    except Invalid:
        return

    g.user.password = request.form['password']
    g.user.recover_key = None

    return redirect(url_for('.index'))


@user_blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not g.user.is_writable(request.identity):
        abort(401)

    if request.method == 'POST':
        result = change_password_post()
        if result:
            return result

    return render_template(
        'generic/form.jinja',
        active_page='settings', title=_('Change Password'),
        form=change_password_form, values={})
