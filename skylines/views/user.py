from datetime import date, timedelta

from flask import Blueprint, render_template, redirect, url_for, g
from flask.ext.login import login_required

from sqlalchemy import func

from skylines import db
from skylines.lib.dbutil import get_requested_record
from skylines.model import (
    User, Flight, Follower, Location, Notification, Event
)
from skylines.model.event import create_follower_notification

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


def mark_user_notifications_read(user):
    if not g.current_user:
        return

    def add_user_filter(query):
        return query.filter(Event.actor_id == user.id)

    Notification.mark_all_read(g.current_user, filter_func=add_user_filter)
    db.session.commit()


@user_blueprint.route('/')
def index():
    mark_user_notifications_read(g.user)

    return render_template(
        'users/view.jinja',
        user=g.user,
        distance_flights=_get_distance_flights(),
        takeoff_locations=_get_takeoff_locations(),
        last_year_statistics=_get_last_year_statistics())


@user_blueprint.route('/follow')
@login_required
def follow():
    Follower.follow(g.current_user, g.user)
    create_follower_notification(g.user, g.current_user)
    db.session.commit()
    return redirect(url_for('.index'))


@user_blueprint.route('/unfollow')
@login_required
def unfollow():
    Follower.unfollow(g.current_user, g.user)
    db.session.commit()
    return redirect(url_for('.index'))
