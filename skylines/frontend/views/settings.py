from flask import Blueprint, request, render_template, redirect, url_for, abort, g, flash, jsonify
from flask.ext.babel import _

from sqlalchemy.sql.expression import and_, or_
from marshmallow import validate

from skylines.database import db
from skylines.frontend.forms import ChangeClubForm, CreateClubForm
from skylines.lib.dbutil import get_requested_record
from skylines.lib.formatter.units import DISTANCE_UNITS, SPEED_UNITS, LIFT_UNITS, ALTITUDE_UNITS
from skylines.model import User, Club, Flight, IGCFile
from skylines.frontend.views.users import send_recover_mail
from skylines.model.event import (
    create_club_join_event
)

settings_blueprint = Blueprint('settings', 'skylines')
email_validator = validate.Email()


@settings_blueprint.before_request
def handle_user_param():
    """
    Extracts the `user` parameter from request.values, queries the
    corresponding User model and checks if the model is writeable by the
    current user.
    """

    if not g.current_user:
        abort(401)

    g.user_id = request.values.get('user')

    if g.user_id:
        g.user = get_requested_record(User, g.user_id)
    else:
        g.user = g.current_user

    if not g.user.is_writable(g.current_user):
        abort(403)

    g.logout_next = url_for("index")


@settings_blueprint.route('/')
def index():
    """ Redirects /settings/ to /settings/profile """
    return redirect(url_for('.profile', user=g.user_id))


@settings_blueprint.route('/profile')
def profile():
    return render_template('settings/profile.jinja')


@settings_blueprint.route('/profile', methods=['POST'])
def change_profile():
    email = request.form.get('email')
    if email is not None and email != g.user.email_address:
        try:
            email_validator(email)
        except:
            return jsonify(error='invalid-email'), 400

        if User.exists(email_address=email):
            return jsonify(error='email-exists-already'), 400

        g.user.email_address = email

    first_name = request.form.get('firstName')
    if first_name is not None:
        if first_name.strip() == '':
            return jsonify(error='invalid-first-name'), 400

        g.user.first_name = first_name

    last_name = request.form.get('lastName')
    if last_name is not None:
        if last_name.strip() == '':
            return jsonify(error='invalid-last-name'), 400

        g.user.last_name = last_name

    distance_unit = request.form.get('distanceUnitIndex')
    if distance_unit is not None:
        distance_unit = int(distance_unit)
        if not (0 <= distance_unit < len(DISTANCE_UNITS)):
            return jsonify(error='invalid-distance-unit'), 400

        g.user.distance_unit = distance_unit

    speed_unit = request.form.get('speedUnitIndex')
    if speed_unit is not None:
        speed_unit = int(speed_unit)
        if not (0 <= speed_unit < len(SPEED_UNITS)):
            return jsonify(error='invalid-speed-unit'), 400

        g.user.speed_unit = speed_unit

    lift_unit = request.form.get('liftUnitIndex')
    if lift_unit is not None:
        lift_unit = int(lift_unit)
        if not (0 <= lift_unit < len(LIFT_UNITS)):
            return jsonify(error='invalid-lift-unit'), 400

        g.user.lift_unit = lift_unit

    altitude_unit = request.form.get('altitudeUnitIndex')
    if altitude_unit is not None:
        altitude_unit = int(altitude_unit)
        if not (0 <= altitude_unit < len(ALTITUDE_UNITS)):
            return jsonify(error='invalid-altitude-unit'), 400

        g.user.altitude_unit = altitude_unit

    db.session.commit()

    return jsonify()


@settings_blueprint.route('/password')
def password():
    return render_template('settings/password.jinja')


@settings_blueprint.route('/password', methods=['POST'])
def change_password():
    if not g.user.validate_password(request.form.get('currentPassword', '')):
        return jsonify(), 403

    password = request.form.get('password', '')
    if len(password) < 6:
        return jsonify(), 400

    g.user.password = password
    g.user.recover_key = None

    db.session.commit()

    return jsonify()


@settings_blueprint.route('/password/recover')
def password_recover():
    if not g.current_user.is_manager():
        abort(403)

    g.user.generate_recover_key(request.remote_addr)
    send_recover_mail(g.user)
    flash('A password recovery email was sent to that user.')

    db.session.commit()

    return redirect(url_for('.password', user=g.user_id))


@settings_blueprint.route('/tracking')
def tracking():
    return render_template('settings/tracking.jinja')


@settings_blueprint.route('/tracking', methods=['POST'])
def change_tracking_settings():
    callsign = request.form.get('callsign')
    if callsign is not None:
        if not (0 < len(callsign) < 6):
            return jsonify(reason='callsign invalid'), 400

        g.user.tracking_callsign = callsign

    delay = request.form.get('delay')
    if delay is not None:
        delay = int(delay)
        if not (0 <= delay <= 60):
            return jsonify(reason='delay invalid'), 400

        g.user.tracking_delay = delay

    db.session.commit()

    return jsonify()


@settings_blueprint.route('/tracking/key', methods=['POST'])
def tracking_generate_key():
    g.user.generate_tracking_key()
    db.session.commit()

    return jsonify(key=g.user.tracking_key_hex)


@settings_blueprint.route('/club', methods=['GET'])
def club():
    change_form = ChangeClubForm(club=g.user.club_id)
    create_form = CreateClubForm()

    if request.endpoint.endswith('.club_change'):
        if change_form.validate_on_submit():
            return club_change_post(change_form)

    if request.endpoint.endswith('.club_create'):
        if create_form.validate_on_submit():
            return club_create_post(create_form)

    return render_template(
        'settings/club.jinja',
        change_form=change_form, create_form=create_form)


@settings_blueprint.route('/club', methods=['POST'])
def club_change():
    return club()


@settings_blueprint.route('/club/create', methods=['POST'])
def club_create():
    return club()


def club_change_post(form):
    old_club_id = g.user.club_id
    new_club_id = form.club.data if form.club.data != 0 else None

    if old_club_id == new_club_id:
        return redirect(url_for('.club', user=g.user_id))

    g.user.club_id = new_club_id

    create_club_join_event(new_club_id, g.user)

    # assign the user's new club to all of his flights that have
    # no club yet
    flights = Flight.query().join(IGCFile)
    flights = flights.filter(and_(Flight.club_id == None,
                                  or_(Flight.pilot_id == g.user.id,
                                      IGCFile.owner_id == g.user.id)))
    for flight in flights:
        flight.club_id = g.user.club_id

    db.session.commit()

    flash(_('New club was saved.'), 'success')

    return redirect(url_for('.club', user=g.user_id))


def club_create_post(form):
    club = Club(name=form.name.data)
    club.owner_id = g.current_user.id
    db.session.add(club)

    db.session.flush()

    g.user.club = club

    create_club_join_event(club.id, g.user)

    db.session.commit()

    return redirect(url_for('.club', user=g.user_id))
