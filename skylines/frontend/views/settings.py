from flask import Blueprint, request, render_template, redirect, url_for, abort, g, flash, jsonify

from sqlalchemy.sql.expression import and_, or_

from skylines.database import db
from skylines.lib.dbutil import get_requested_record
from skylines.lib.vary import vary
from skylines.model import User, Club, Flight, IGCFile
from skylines.frontend.views.users import send_recover_mail
from skylines.model.event import (
    create_club_join_event
)
from skylines.schemas import fields, validate, Schema, ClubSchema, UserSchema, ValidationError

settings_blueprint = Blueprint('settings', 'skylines')


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

    schema = UserSchema(only=('email', 'firstName', 'lastName', 'distanceUnit', 'speedUnit', 'liftUnit', 'altitudeUnit'))
    return jsonify(**schema.dump(g.user).data)


@settings_blueprint.route('/profile', methods=['POST'])
def change_profile():
    json = request.get_json()
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = UserSchema(partial=True).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    if 'email_address' in data:
        email = data.get('email_address')

        if email != g.user.email_address and User.exists(email_address=email):
            return jsonify(error='email-exists-already'), 422

        g.user.email_address = email

    if 'first_name' in data:
        g.user.first_name = data.get('first_name')

    if 'last_name' in data:
        g.user.last_name = data.get('last_name')

    if 'distance_unit' in data:
        g.user.distance_unit = data.get('distance_unit')

    if 'speed_unit' in data:
        g.user.speed_unit = data.get('speed_unit')

    if 'lift_unit' in data:
        g.user.lift_unit = data.get('lift_unit')

    if 'altitude_unit' in data:
        g.user.altitude_unit = data.get('altitude_unit')

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
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = PasswordSchema().load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    if not g.user.validate_password(data.get('currentPassword')):
        return jsonify(error='wrong-password'), 403

    g.user.password = data.get('password')
    g.user.recover_key = None

    db.session.commit()

    return jsonify()


class PasswordSchema(Schema):
    password = fields.String(required=True, validate=validate.Length(min=6))
    currentPassword = fields.String(required=True)


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
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = UserSchema(only=('trackingCallsign', 'trackingDelay')).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    if 'tracking_callsign' in data:
        g.user.tracking_callsign = data.get('tracking_callsign')

    if 'tracking_delay' in data:
        g.user.tracking_delay = data.get('tracking_delay')

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
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = ChooseClubSchema().load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    id = data.get('id')
    if g.user.club_id == id:
        return jsonify()

    if id is not None and not Club.exists(id=id):
        return jsonify(error='unknown-club'), 422

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


class ChooseClubSchema(Schema):
    id = fields.Integer(required=True, allow_none=True)


@settings_blueprint.route('/club', methods=['PUT'])
def create_club():
    json = request.get_json()
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = ClubSchema(only=('name',)).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    if Club.exists(name=data.get('name')):
        return jsonify(error='duplicate-club-name'), 422

    # create the new club
    club = Club(**data)
    club.owner_id = g.current_user.id
    db.session.add(club)
    db.session.flush()

    # assign the user to the new club
    g.user.club = club

    # create the "user joined club" event
    create_club_join_event(club.id, g.user)

    db.session.commit()

    return jsonify(id=club.id)
