from datetime import datetime

from flask import Blueprint, request, current_app, render_template
from flask.ext.login import current_user
from werkzeug.exceptions import BadRequest, NotFound, NotImplemented

from skylines.model import User, TrackingFix, Airport

tracking_blueprint = Blueprint('tracking', 'skylines')


@tracking_blueprint.route('/')
def index():
    tracks = TrackingFix.get_latest()

    @current_app.cache.memoize(timeout=60*60)
    def get_nearest_airport(track):
        airport = Airport.by_location(track.location, None)
        if not airport:
            return None

        distance = airport.distance(track.location)

        return {
            'name': airport.name,
            'country_code': airport.country_code,
            'distance': distance,
        }

    tracks = [(track, get_nearest_airport(track)) for track in tracks]

    return render_template('tracking/list.jinja', tracks=tracks)


@tracking_blueprint.route('/info')
def info():
    user = None
    if not current_user.is_anonymous():
        user = current_user

    return render_template('tracking/info.jinja', user=user)
