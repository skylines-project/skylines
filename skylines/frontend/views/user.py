from datetime import date, timedelta

from flask import Blueprint, request

from sqlalchemy import func, and_
from sqlalchemy.orm import contains_eager, subqueryload

from skylines.api.json import jsonify
from skylines.database import db
from skylines.frontend.oauth import oauth
from skylines.lib.dbutil import get_requested_record
from skylines.model import (
    User, Flight, Follower, Location, Notification, Event
)
from skylines.model.event import create_follower_notification
from skylines.schemas import Schema, fields, FlightSchema, CurrentUserSchema, UserSchema

user_blueprint = Blueprint('user', 'skylines')


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


@user_blueprint.route('/users/<user_id>', strict_slashes=False)
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


@user_blueprint.route('/users/<user_id>/followers')
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


@user_blueprint.route('/users/<user_id>/following')
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


@user_blueprint.route('/users/<user_id>/follow')
@oauth.required()
def follow(user_id):
    user = get_requested_record(User, user_id)
    current_user = User.get(request.user_id)
    Follower.follow(current_user, user)
    create_follower_notification(user, current_user)
    db.session.commit()
    return jsonify()


@user_blueprint.route('/users/<user_id>/unfollow')
@oauth.required()
def unfollow(user_id):
    user = get_requested_record(User, user_id)
    current_user = User.get(request.user_id)
    Follower.unfollow(current_user, user)
    db.session.commit()
    return jsonify()
