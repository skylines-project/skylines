from flask import Blueprint, request
from sqlalchemy.sql.expression import and_, or_

from skylines.api.json import jsonify
from skylines.api.oauth import oauth
from skylines.database import db
from skylines.model import User, Club, Flight, IGCFile
from skylines.model.event import (
    create_club_join_event
)
from skylines.schemas import ClubSchema, CurrentUserSchema, ValidationError

settings_blueprint = Blueprint('settings', 'skylines')


@settings_blueprint.route('/settings', strict_slashes=False)
@oauth.required()
def read():
    current_user = User.get(request.user_id)
    if not current_user:
        return jsonify(error='invalid-token'), 401

    schema = CurrentUserSchema(exclude=('id'))
    return jsonify(schema.dump(current_user).data)


@settings_blueprint.route('/settings', methods=['POST'], strict_slashes=False)
@oauth.required()
def update():
    current_user = User.get(request.user_id)
    if not current_user:
        return jsonify(error='invalid-token'), 401

    json = request.get_json()
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = CurrentUserSchema(partial=True).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    if 'email_address' in data:
        email = data.get('email_address')

        if email != current_user.email_address and User.exists(email_address=email):
            return jsonify(error='email-exists-already'), 422

        current_user.email_address = email

    if 'first_name' in data:
        current_user.first_name = data.get('first_name')

    if 'last_name' in data:
        current_user.last_name = data.get('last_name')

    if 'distance_unit' in data:
        current_user.distance_unit = data.get('distance_unit')

    if 'speed_unit' in data:
        current_user.speed_unit = data.get('speed_unit')

    if 'lift_unit' in data:
        current_user.lift_unit = data.get('lift_unit')

    if 'altitude_unit' in data:
        current_user.altitude_unit = data.get('altitude_unit')

    if 'tracking_callsign' in data:
        current_user.tracking_callsign = data.get('tracking_callsign')

    if 'tracking_delay' in data:
        current_user.tracking_delay = data.get('tracking_delay')

    if 'password' in data:
        if 'currentPassword' not in data:
            return jsonify(error='current-password-missing'), 422

        if not current_user.validate_password(data['currentPassword']):
            return jsonify(error='wrong-password'), 403

        current_user.password = data['password']
        current_user.recover_key = None

    if 'club_id' in data and data['club_id'] != current_user.club_id:
        club_id = data['club_id']

        if club_id is not None and not Club.exists(id=club_id):
            return jsonify(error='unknown-club'), 422

        current_user.club_id = club_id

        create_club_join_event(club_id, current_user)

        # assign the user's new club to all of his flights that have
        # no club yet
        flights = Flight.query().join(IGCFile)
        flights = flights.filter(and_(Flight.club_id == None,
                                      or_(Flight.pilot_id == current_user.id,
                                          IGCFile.owner_id == current_user.id)))
        for flight in flights:
            flight.club_id = club_id

    db.session.commit()

    return jsonify()


@settings_blueprint.route('/settings/password/check', methods=['POST'])
@oauth.required()
def check_current_password():
    current_user = User.get(request.user_id)
    if not current_user:
        return jsonify(error='invalid-token'), 401

    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    return jsonify(result=current_user.validate_password(json.get('password', '')))


@settings_blueprint.route('/settings/tracking/key', methods=['POST'])
@oauth.required()
def tracking_generate_key():
    current_user = User.get(request.user_id)
    if not current_user:
        return jsonify(error='invalid-token'), 401

    current_user.generate_tracking_key()
    db.session.commit()

    return jsonify(key=current_user.tracking_key_hex)


@settings_blueprint.route('/settings/club', methods=['PUT'])
@oauth.required()
def create_club():
    current_user = User.get(request.user_id)
    if not current_user:
        return jsonify(error='invalid-token'), 401

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
    club.owner_id = current_user.id
    db.session.add(club)
    db.session.flush()

    # assign the user to the new club
    current_user.club = club

    # create the "user joined club" event
    create_club_join_event(club.id, current_user)

    db.session.commit()

    return jsonify(id=club.id)
