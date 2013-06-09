from flask import Blueprint, current_app, render_template, jsonify, g

from skylines.lib.helpers import isoformat_utc
from skylines.lib.decorators import jsonp
from skylines.model import TrackingFix, Airport

tracking_blueprint = Blueprint('tracking', 'skylines')


@tracking_blueprint.route('/')
def index():
    tracks = TrackingFix.get_latest()

    @current_app.cache.memoize(timeout=(60 * 60))
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
    return render_template('tracking/info.jinja', user=g.current_user)


@tracking_blueprint.route('/latest.json')
@jsonp
def latest():
    fixes = []
    for fix in TrackingFix.get_latest():
        json = dict(time=isoformat_utc(fix.time),
                    location=fix.location.to_wkt(),
                    pilot=dict(id=fix.pilot_id, name=unicode(fix.pilot)))

        optional_attributes = ['track', 'ground_speed', 'airspeed',
                               'altitude', 'vario', 'engine_noise_level']
        for attr in optional_attributes:
            value = getattr(fix, attr)
            if value is not None:
                json[attr] = value

        fixes.append(json)

    return jsonify(fixes=fixes)
