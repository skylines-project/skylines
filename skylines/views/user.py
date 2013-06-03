from datetime import date, timedelta

from flask import Blueprint, request, render_template, redirect, url_for, abort, g, flash
from flask.ext.babel import lazy_gettext as l_, _, ngettext
from flask.ext.login import login_required, current_user

from formencode import Schema, All
from formencode.validators import FieldsMatch, Email, NotEmpty
from sprox.formbase import EditableForm, Field
from sprox.widgets import PropertySingleSelectField
from tw.forms import PasswordField, TextField, CheckBox
from tw.forms.validators import UnicodeString

from sqlalchemy.sql.expression import and_, or_
from sqlalchemy import func

from skylines import db
from skylines.forms import BootstrapForm, units, club
from skylines.lib.validators import UniqueValueUnless
from skylines.lib.dbutil import get_requested_record
from skylines.lib.decorators import validate
from skylines.model import (
    User, Club, Flight, Follower, Location, IGCFile
)
from skylines.model.notification import create_follower_notification
from skylines.views.users import recover_user_password

user_blueprint = Blueprint('user', 'skylines')


@user_blueprint.url_value_preprocessor
def _pull_user_id(endpoint, values):
    g.user_id = values.pop('user_id')
    g.user = get_requested_record(User, g.user_id)


@user_blueprint.url_defaults
def _add_user_id(endpoint, values):
    if hasattr(g, 'user_id'):
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
    query = db.session.query(func.count('*').label('flights'),
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


@user_blueprint.route('/change_password')
def change_password():
    if not g.user.is_writable(request.identity):
        abort(403)

    return render_template(
        'generic/form.jinja',
        active_page='settings', title=_('Change Password'),
        form=change_password_form, values={})


@user_blueprint.route('/change_password', methods=['POST'])
@validate(change_password_form, change_password)
def change_password_post():
    if not g.user.is_writable(request.identity):
        abort(403)

    g.user.password = request.form['password']
    g.user.recover_key = None

    db.session.commit()

    return redirect(url_for('.index'))


class DelaySelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        options = [(0, _('None'))]
        for x in range(1, 10) + range(10, 30, 5) + range(30, 61, 15):
            options.append((x, ngettext(u'%(num)u minute', u'%(num)u minutes', x)))
        d['options'] = options
        return d


def filter_user_id(model):
    return model.id == g.user.id


class EditUserForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = User
    __hide_fields__ = ['id']
    __limit_fields__ = ['email_address', 'name',
                        'tracking_delay', 'unit_preset',
                        'distance_unit', 'speed_unit',
                        'lift_unit', 'altitude_unit',
                        'eye_candy']
    __field_widget_args__ = {
        'email_address': dict(label_text=l_('eMail Address')),
        'name': dict(label_text=l_('Name')),
        'tracking_delay': dict(label_text=l_('Tracking Delay')),
        'unit_preset': dict(label_text=l_('Unit Preset')),
        'distance_unit': dict(label_text=l_('Distance Unit')),
        'speed_unit': dict(label_text=l_('Speed Unit')),
        'lift_unit': dict(label_text=l_('Lift Unit')),
        'altitude_unit': dict(label_text=l_('Altitude Unit')),
        'eye_candy': dict(label_text=l_('Eye Candy')),
    }

    email_address = Field(TextField, All(
        Email(not_empty=True),
        UniqueValueUnless(filter_user_id, db.session, __model__, 'email_address')))
    name = Field(TextField, NotEmpty)
    tracking_delay = DelaySelectField
    unit_preset = units.PresetSelectField("unit_preset")
    distance_unit = units.DistanceSelectField
    speed_unit = units.SpeedSelectField
    lift_unit = units.LiftSelectField
    altitude_unit = units.AltitudeSelectField
    eye_candy = Field(CheckBox)

edit_user_form = EditUserForm(db.session)


@user_blueprint.route('/edit')
def edit():
    if not g.user.is_writable(request.identity):
        abort(403)

    return render_template(
        'generic/form.jinja',
        active_page='settings', title=_('Edit User'),
        form=edit_user_form, values=g.user,
        include_script='users/after-edit-form.jinja')


@user_blueprint.route('/edit', methods=['POST'])
@validate(edit_user_form, edit)
def edit_post():
    if not g.user.is_writable(request.identity):
        abort(403)

    g.user.email_address = request.form['email_address']
    g.user.name = request.form['name']
    g.user.tracking_delay = request.form.get('tracking_delay', 0)

    unit_preset = request.form.get('unit_preset', 1, type=int)
    if unit_preset == 0:
        g.user.distance_unit = request.form.get('distance_unit', 1, type=int)
        g.user.speed_unit = request.form.get('speed_unit', 1, type=int)
        g.user.lift_unit = request.form.get('lift_unit', 0, type=int)
        g.user.altitude_unit = request.form.get('altitude_unit', 0, type=int)
    else:
        g.user.unit_preset = unit_preset

    g.user.eye_candy = request.form.get('eye_candy', False, type=bool)

    db.session.commit()

    return redirect(url_for('.index'))


@user_blueprint.route('/change_club')
def change_club():
    if not g.user.is_writable(request.identity):
        abort(403)

    return render_template(
        'users/change_club.jinja', user=g.user,
        select_form=club.select_form, create_form=club.new_form)


@user_blueprint.route('/change_club', methods=['POST'])
@validate(club.select_form, change_club)
def change_club_post():
    if not g.user.is_writable(request.identity):
        abort(403)

    g.user.club_id = request.form['club']

    # assign the user's new club to all of his flights that have
    # no club yet
    flights = Flight.query().join(IGCFile)
    flights = flights.filter(and_(Flight.club_id == None,
                                  or_(Flight.pilot_id == g.user.id,
                                      IGCFile.owner_id == g.user.id)))
    for flight in flights:
        flight.club_id = club

    db.session.commit()

    return redirect(url_for('.index'))


@user_blueprint.route('/create_club', methods=['POST'])
@validate(club.new_form, change_club)
def create_club_post():
    if not g.user.is_writable(request.identity):
        abort(403)

    club = Club(name=request.form['name'])
    club.owner_id = current_user.id
    db.session.add(club)

    g.user.club = club

    db.session.commit()

    return redirect(url_for('.index'))


@user_blueprint.route('/follow')
@login_required
def follow():
    Follower.follow(current_user, g.user)
    create_follower_notification(g.user, current_user)
    db.session.commit()
    return redirect(url_for('.index'))


@user_blueprint.route('/unfollow')
@login_required
def unfollow():
    Follower.unfollow(current_user, g.user)
    db.session.commit()
    return redirect(url_for('.index'))


@user_blueprint.route('/tracking_register')
def tracking_register():
    if not g.user.is_writable(request.identity):
        abort(403)

    g.user.generate_tracking_key()
    db.session.commit()

    return redirect(request.values.get('came_from', '/tracking/info'))


@user_blueprint.route('/recover_password')
def recover_password():
    if not request.identity or 'manage' not in request.identity['permissions']:
        abort(403)

    recover_user_password(g.user)
    flash('A password recovery email was sent to that user.')

    db.session.commit()

    return redirect(url_for('.index'))
