from datetime import date, timedelta

from flask import Blueprint, render_template, redirect, url_for, g, request, jsonify
from flask.ext.login import login_required

from sqlalchemy import func, and_
from sqlalchemy.orm import contains_eager, subqueryload

from skylines.database import db
from skylines.lib.dbutil import get_requested_record
from skylines.lib.vary import vary
from skylines.model import (
    User, Flight, Follower, Location, Notification, Event
)
from skylines.model.event import create_follower_notification
from skylines.schemas import Schema, fields, FlightSchema, CurrentUserSchema, UserSchema

user_blueprint = Blueprint('user', 'skylines')


@user_blueprint.url_value_preprocessor
def _pull_user_id(endpoint, values):
    g.user_id = values.pop('user_id')
    g.user = get_requested_record(User, g.user_id)


@user_blueprint.url_defaults
def _add_user_id(endpoint, values):
    if hasattr(g, 'user_id'):
        values.setdefault('user_id', g.user_id)


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


def _quick_stats():
    result = db.session.query(func.count('*').label('flights'),
                              func.sum(Flight.olc_classic_distance).label('distance'),
                              func.sum(Flight.duration).label('duration')) \
        .filter(Flight.pilot == g.user) \
        .filter(Flight.date_local > (date.today() - timedelta(days=365))) \
        .filter(Flight.is_rankable()) \
        .one()

    return QuickStatsSchema().dump(result).data


def _get_takeoff_locations():
    locations = Location.get_clustered_locations(
        Flight.takeoff_location_wkt, filter=and_(Flight.pilot == g.user, Flight.is_rankable()))

    return [loc.to_lonlat() for loc in locations]


def mark_user_notifications_read(user):
    if not g.current_user:
        return

    def add_user_filter(query):
        return query.filter(Event.actor_id == user.id)

    Notification.mark_all_read(g.current_user, filter_func=add_user_filter)
    db.session.commit()


@user_blueprint.route('/')
@vary('accept')
def index():
    if 'application/json' in request.headers.get('Accept', ''):
        user_schema = CurrentUserSchema() if g.user == g.current_user else UserSchema()
        user = user_schema.dump(g.user).data

        if g.current_user:
            user['followed'] = g.current_user.follows(g.user)

        if 'extended' in request.args:
            user['distanceFlights'] = _distance_flights(g.user)
            user['stats'] = _quick_stats()
            user['takeoffLocations'] = _get_takeoff_locations()

        return jsonify(**user)

    mark_user_notifications_read(g.user)

    return render_template('ember-page.jinja', openlayers=True, active_page='settings')


@user_blueprint.route('/followers')
def followers():
    # Query list of pilots that are following the selected user
    query = Follower.query(destination=g.user) \
        .join('source') \
        .options(contains_eager('source')) \
        .options(subqueryload('source.club')) \
        .order_by(User.name)

    followers = UserSchema(only=('id', 'name', 'club'))\
        .dump([follower.source for follower in query], many=True).data

    add_current_user_follows(followers)

    return render_template('users/followers.jinja', followers=followers)


@user_blueprint.route('/following')
def following():
    # Query list of pilots that are following the selected user
    query = Follower.query(source=g.user) \
        .join('destination') \
        .options(contains_eager('destination')) \
        .options(subqueryload('destination.club')) \
        .order_by(User.name)

    followers = UserSchema(only=('id', 'name', 'club')) \
        .dump([follower.destination for follower in query], many=True).data

    add_current_user_follows(followers)

    return render_template('users/following.jinja', followers=followers)


def add_current_user_follows(followers):
    """
    If the user if signed in the followers will get an additional
    `current_user_follows` attribute, that shows if the signed in user is
    following the pilot
    """

    if not g.current_user:
        return

    # Query list of people that the current user is following
    query = Follower.query(source=g.current_user)
    current_user_follows = [follower.destination_id for follower in query]

    for follower in followers:
        follower['currentUserFollows'] = (follower['id'] in current_user_follows)


@user_blueprint.route('/follow')
@login_required
def follow():
    Follower.follow(g.current_user, g.user)
    create_follower_notification(g.user, g.current_user)
    db.session.commit()
    return redirect(request.referrer or url_for('.index'))


@user_blueprint.route('/unfollow')
@login_required
def unfollow():
    Follower.unfollow(g.current_user, g.user)
    db.session.commit()
    return redirect(request.referrer or url_for('.index'))
