from datetime import date, timedelta
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib

from flask import Blueprint, request, current_app
from werkzeug.exceptions import ServiceUnavailable

from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload, contains_eager, subqueryload

from skylines.api.json import jsonify
from skylines.database import db
from skylines.api.oauth import oauth
from skylines.lib.dbutil import get_requested_record
from skylines.model import (
    User, Flight, Follower, Location, Notification, Event
)
from skylines.model.event import create_new_user_event, create_follower_notification
from skylines.schemas import Schema, fields, FlightSchema, CurrentUserSchema, UserSchema, ValidationError

users_blueprint = Blueprint('users', 'skylines')


@users_blueprint.route('/users', strict_slashes=False)
def list():
    users = User.query() \
        .options(joinedload(User.club)) \
        .order_by(func.lower(User.name))

    fields = ['id', 'name']

    if 'club' in request.args:
        users = users.filter_by(club_id=request.args.get('club'))
    else:
        fields.append('club')

    return jsonify(users=UserSchema(only=fields).dump(users, many=True).data)


@users_blueprint.route('/users', methods=['POST'], strict_slashes=False)
def new_post():
    json = request.get_json()
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = CurrentUserSchema(only=('email', 'firstName', 'lastName', 'password')).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    user = User(**data)

    user.created_ip = request.remote_addr
    db.session.add(user)

    create_new_user_event(user)

    db.session.commit()

    return jsonify(user=UserSchema().dump(user).data)


@users_blueprint.route('/users/recover', methods=['POST'])
def recover_post():
    json = request.get_json()
    if json is None:
        return jsonify(error='invalid-request'), 400

    if 'recoveryKey' in json:
        return recover_step2_post(json)
    else:
        return recover_step1_post(json)


def recover_step1_post(json):
    try:
        data = CurrentUserSchema(only=('email',)).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    user = User.by_email_address(data['email_address'])
    if not user:
        return jsonify(error='email-unknown'), 422

    user.generate_recover_key(request.remote_addr)
    try:
        send_recover_mail(user)
    except ServiceUnavailable:
        return jsonify(error='mail-service-unavailable'), 503

    db.session.commit()

    return jsonify()


def send_recover_mail(user):
    text = u"""Hi %s,

you have asked to recover your password (from IP %s).  To enter a new
password, click on the following link:

 http://skylines.aero/users/recover?key=%x

The SkyLines Team
""" % (unicode(user), request.remote_addr, user.recover_key)

    msg = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    msg['Subject'] = 'SkyLines password recovery'
    msg['From'] = current_app.config['EMAIL_FROM']
    msg['To'] = user.email_address.encode('ascii')
    msg['Date'] = formatdate(localtime=1)

    try:
        smtp = smtplib.SMTP(current_app.config['SMTP_SERVER'])
        smtp.ehlo()
        smtp.sendmail(current_app.config['EMAIL_FROM'].encode('ascii'),
                      user.email_address.encode('ascii'), msg.as_string())
        smtp.quit()

    except:
        raise ServiceUnavailable(description=(
            "The mail server is currently not reachable. "
            "Please try again later or contact the developers."))


def recover_step2_post(json):
    try:
        data = CurrentUserSchema(only=('password', 'recoveryKey')).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    user = User.by_recover_key(int(data['recover_key'], base=16))
    if not user:
        return jsonify(error='recovery-key-unknown'), 422

    user.password = data['password']
    user.recover_key = None

    db.session.commit()

    return jsonify()


@users_blueprint.route('/users/check-email', methods=['POST'])
@oauth.optional()
def check_email():
    current_user = User.get(request.user_id) if request.user_id else None

    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    email = json.get('email', '')

    result = 'available'
    if current_user and email == current_user.email_address:
        result = 'self'
    elif User.exists(email_address=email):
        result = 'unavailable'

    return jsonify(result=result)


def _largest_flight(user, schema):
    flight = user.get_largest_flights() \
        .filter(Flight.is_rankable()) \
        .first()

    if flight:
        return schema.dump(flight).data


def _distance_flight(user, distance, schema):
    flight = Flight.query() \
        .filter(Flight.pilot == user) \
        .filter(Flight.olc_classic_distance >= distance) \
        .order_by(Flight.landing_time) \
        .filter(Flight.is_rankable()) \
        .first()

    if flight:
        return schema.dump(flight).data


def _distance_flights(user):
    schema = FlightSchema(only=('id', 'scoreDate', 'distance'))

    return {
        '50km': _distance_flight(user, 50000, schema),
        '100km': _distance_flight(user, 100000, schema),
        '300km': _distance_flight(user, 300000, schema),
        '500km': _distance_flight(user, 500000, schema),
        '700km': _distance_flight(user, 700000, schema),
        '1000km': _distance_flight(user, 1000000, schema),
        'largest': _largest_flight(user, schema),
    }


class QuickStatsSchema(Schema):
    flights = fields.Int()
    distance = fields.Float()
    duration = fields.TimeDelta()


def _quick_stats(user):
    result = db.session.query(func.count('*').label('flights'),
                              func.sum(Flight.olc_classic_distance).label('distance'),
                              func.sum(Flight.duration).label('duration')) \
        .filter(Flight.pilot == user) \
        .filter(Flight.date_local > (date.today() - timedelta(days=365))) \
        .filter(Flight.is_rankable()) \
        .one()

    return QuickStatsSchema().dump(result).data


def _get_takeoff_locations(user):
    locations = Location.get_clustered_locations(
        Flight.takeoff_location_wkt, filter=and_(Flight.pilot == user, Flight.is_rankable()))

    return [loc.to_lonlat() for loc in locations]


def mark_user_notifications_read(user):
    if not request.user_id:
        return

    def add_user_filter(query):
        return query.filter(Event.actor_id == user.id)

    Notification.mark_all_read(User.get(request.user_id), filter_func=add_user_filter)
    db.session.commit()


@users_blueprint.route('/users/<user_id>', strict_slashes=False)
@oauth.optional()
def read(user_id):
    user = get_requested_record(User, user_id)

    user_schema = CurrentUserSchema() if user_id == request.user_id else UserSchema()
    user_json = user_schema.dump(user).data

    if request.user_id:
        current_user = User.get(request.user_id)
        user_json['followed'] = current_user.follows(user)

    if 'extended' in request.args:
        user_json['distanceFlights'] = _distance_flights(user)
        user_json['stats'] = _quick_stats(user)
        user_json['takeoffLocations'] = _get_takeoff_locations(user)

    mark_user_notifications_read(user)

    return jsonify(user_json)


@users_blueprint.route('/users/<user_id>/followers')
@oauth.optional()
def followers(user_id):
    user = get_requested_record(User, user_id)

    # Query list of pilots that are following the selected user
    query = Follower.query(destination=user) \
        .join('source') \
        .options(contains_eager('source')) \
        .options(subqueryload('source.club')) \
        .order_by(User.name)

    user_schema = UserSchema(only=('id', 'name', 'club'))
    followers = user_schema.dump([follower.source for follower in query], many=True).data

    add_current_user_follows(followers)

    return jsonify(followers=followers)


@users_blueprint.route('/users/<user_id>/following')
@oauth.optional()
def following(user_id):
    user = get_requested_record(User, user_id)

    # Query list of pilots that are following the selected user
    query = Follower.query(source=user) \
        .join('destination') \
        .options(contains_eager('destination')) \
        .options(subqueryload('destination.club')) \
        .order_by(User.name)

    user_schema = UserSchema(only=('id', 'name', 'club'))

    following = user_schema.dump([follower.destination for follower in query], many=True).data

    add_current_user_follows(following)

    return jsonify(following=following)


def add_current_user_follows(followers):
    """
    If the user if signed in the followers will get an additional
    `current_user_follows` attribute, that shows if the signed in user is
    following the pilot
    """

    if not request.user_id:
        return

    # Query list of people that the current user is following
    query = Follower.query(source_id=request.user_id)
    current_user_follows = [follower.destination_id for follower in query]

    for follower in followers:
        follower['currentUserFollows'] = (follower['id'] in current_user_follows)


@users_blueprint.route('/users/<user_id>/follow')
@oauth.required()
def follow(user_id):
    user = get_requested_record(User, user_id)
    current_user = User.get(request.user_id)
    Follower.follow(current_user, user)
    create_follower_notification(user, current_user)
    db.session.commit()
    return jsonify()


@users_blueprint.route('/users/<user_id>/unfollow')
@oauth.required()
def unfollow(user_id):
    user = get_requested_record(User, user_id)
    current_user = User.get(request.user_id)
    Follower.unfollow(current_user, user)
    db.session.commit()
    return jsonify()
