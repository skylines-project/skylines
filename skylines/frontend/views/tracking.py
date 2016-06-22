from flask import Blueprint, current_app, render_template, jsonify, g, request

from skylines.lib.helpers import isoformat_utc
from skylines.lib.decorators import jsonp
from skylines.lib.vary import vary_accept
from skylines.model import TrackingFix, Airport, Follower

tracking_blueprint = Blueprint('tracking', 'skylines')


@tracking_blueprint.route('/')
@vary_accept
def index():
    if 'application/json' not in request.headers.get('Accept', ''):
        return render_template('ember-page.jinja', active_page='tracking')

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

    def convert(track, airport):
        location = None
        if track.location_wkt is not None:
            location = track.location.to_lonlat()

        return {
            'time': track.time.isoformat(),
            'pilot': {
                'id': track.pilot_id,
                'name': unicode(track.pilot),
            },
            'airport': airport,
            'location': location,
            'altitude': track.altitude,
            'elevation': track.elevation
        }

    tracks = [convert(track, get_nearest_airport(track)) for track in tracks]

    if g.current_user:
        followers = [f.destination_id for f in Follower.query(source=g.current_user)]
    else:
        followers = []

    return jsonify(friends=followers, tracks=tracks)



@tracking_blueprint.route('/info')
def info():
    return render_template('tracking/info.jinja')


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
