from flask import Blueprint, current_app, render_template, jsonify, g

from skylines.lib.helpers import isoformat_utc
from skylines.lib.decorators import jsonp
from skylines.model import TrackingFix, Airport, Follower

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

    if g.current_user:
        followers = [f.destination_id for f in Follower.query(source=g.current_user)]

        def is_self_or_follower(track):
            pilot_id = track[0].pilot_id
            return pilot_id == g.current_user.id or pilot_id in followers

        friend_tracks = [t for t in tracks if is_self_or_follower(t)]
        other_tracks = [t for t in tracks if t not in friend_tracks]

    else:
        friend_tracks = []
        other_tracks = tracks

    return render_template('tracking/list.jinja',
                           friend_tracks=friend_tracks,
                           other_tracks=other_tracks)


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
