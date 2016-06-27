from flask import Blueprint, request, render_template, redirect, url_for, abort, g, flash, jsonify

from sqlalchemy.sql.expression import and_, or_
from marshmallow import validate

from skylines.database import db
from skylines.lib.dbutil import get_requested_record
from skylines.lib.vary import vary
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
@vary('accept')
def profile():
    if 'application/json' not in request.headers.get('Accept', ''):
        return render_template('ember-page.jinja', active_page='settings')

    return jsonify(
        email=g.user.email_address,
        firstName=g.user.first_name,
        lastName=g.user.last_name,
        distanceUnitIndex=g.user.distance_unit,
        speedUnitIndex=g.user.speed_unit,
        liftUnitIndex=g.user.lift_unit,
        altitudeUnitIndex=g.user.altitude_unit,
    )


@settings_blueprint.route('/profile', methods=['POST'])
def change_profile():
    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    email = json.get('email')
    if email is not None and email != g.user.email_address:
        try:
            email_validator(email)
        except:
            return jsonify(error='invalid-email'), 422

        if User.exists(email_address=email):
            return jsonify(error='email-exists-already'), 422

        g.user.email_address = email

    first_name = json.get('firstName')
    if first_name is not None:
        if first_name.strip() == '':
            return jsonify(error='invalid-first-name'), 422

        g.user.first_name = first_name

    last_name = json.get('lastName')
    if last_name is not None:
        if last_name.strip() == '':
            return jsonify(error='invalid-last-name'), 422

        g.user.last_name = last_name

    distance_unit = json.get('distanceUnitIndex')
    if distance_unit is not None:
        distance_unit = int(distance_unit)
        if not (0 <= distance_unit < len(DISTANCE_UNITS)):
            return jsonify(error='invalid-distance-unit'), 422

        g.user.distance_unit = distance_unit

    speed_unit = json.get('speedUnitIndex')
    if speed_unit is not None:
        speed_unit = int(speed_unit)
        if not (0 <= speed_unit < len(SPEED_UNITS)):
            return jsonify(error='invalid-speed-unit'), 422

        g.user.speed_unit = speed_unit

    lift_unit = json.get('liftUnitIndex')
    if lift_unit is not None:
        lift_unit = int(lift_unit)
        if not (0 <= lift_unit < len(LIFT_UNITS)):
            return jsonify(error='invalid-lift-unit'), 422

        g.user.lift_unit = lift_unit

    altitude_unit = json.get('altitudeUnitIndex')
    if altitude_unit is not None:
        altitude_unit = int(altitude_unit)
        if not (0 <= altitude_unit < len(ALTITUDE_UNITS)):
            return jsonify(error='invalid-altitude-unit'), 422

        g.user.altitude_unit = altitude_unit

    db.session.commit()

    return jsonify()


@settings_blueprint.route('/email/check', methods=['POST'])
def check_email():
    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    email = json.get('email', '')
    return jsonify(result=(email == g.user.email_address or not User.exists(email_address=email)))


@settings_blueprint.route('/password')
def password():
    return render_template('ember-page.jinja', active_page='settings')


@settings_blueprint.route('/password', methods=['POST'])
def change_password():
    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    if not g.user.validate_password(json.get('currentPassword', '')):
        return jsonify(), 403

    password = json.get('password', '')
    if len(password) < 6:
        return jsonify(), 422

    g.user.password = password
    g.user.recover_key = None

    db.session.commit()

    return jsonify()


@settings_blueprint.route('/password/check', methods=['POST'])
def check_current_password():
    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    return jsonify(result=g.user.validate_password(json.get('password', '')))


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
@vary('accept')
def tracking():
    if 'application/json' not in request.headers.get('Accept', ''):
        return render_template('ember-page.jinja', active_page='settings')

    return jsonify(
        key=g.user.tracking_key_hex,
        delay=g.user.tracking_delay,
        callsign=g.user.tracking_callsign,
    )


@settings_blueprint.route('/tracking', methods=['POST'])
def change_tracking_settings():
    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    callsign = json.get('callsign')
    if callsign is not None:
        if not (0 < len(callsign) < 6):
            return jsonify(reason='callsign invalid'), 422

        g.user.tracking_callsign = callsign

    delay = json.get('delay')
    if delay is not None:
        delay = int(delay)
        if not (0 <= delay <= 60):
            return jsonify(reason='delay invalid'), 422

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
    return render_template('ember-page.jinja', active_page='settings')


@settings_blueprint.route('/club', methods=['POST'])
def club_change():
    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    if 'id' not in json:
        return jsonify(error='missing-id'), 422

    id = json.get('id')
    if id is not None:
        id = int(id)

        if not Club.exists(id=id):
            return jsonify(error='club-does-not-exist'), 422

    if g.user.club_id == id:
        return jsonify()

    g.user.club_id = id

    create_club_join_event(id, g.user)

    # assign the user's new club to all of his flights that have
    # no club yet
    flights = Flight.query().join(IGCFile)
    flights = flights.filter(and_(Flight.club_id == None,
                                  or_(Flight.pilot_id == g.user.id,
                                      IGCFile.owner_id == g.user.id)))
    for flight in flights:
        flight.club_id = id

    db.session.commit()
    return jsonify()


@settings_blueprint.route('/club', methods=['PUT'])
def create_club():
    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    name = json.get('name')
    if name is None:
        return jsonify(error='missing-name'), 400

    name = name.strip()
    if name == '':
        return jsonify(error='invalid-name'), 422

    if Club.exists(name=name):
        return jsonify(error='club-exists'), 422

    # create the new club
    club = Club(name=name)
    club.owner_id = g.current_user.id
    db.session.add(club)
    db.session.flush()

    # assign the user to the new club
    g.user.club = club

    # create the "user joined club" event
    create_club_join_event(club.id, g.user)

    db.session.commit()

    return jsonify(id=club.id)
