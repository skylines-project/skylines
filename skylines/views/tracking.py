from datetime import datetime

from flask import Blueprint, request, current_app, render_template
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
