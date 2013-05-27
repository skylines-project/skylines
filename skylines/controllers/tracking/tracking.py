from tg import expose, request, cache
from webob.exc import HTTPNotFound

from . import TrackController
from skylines.controllers.base import BaseController
from skylines.lib.dbutil import get_requested_record_list
from skylines.lib.helpers import isoformat_utc
from skylines.lib.decorators import jsonp
from skylines.model import User, TrackingFix, Airport


class TrackingController(BaseController):
    @expose('tracking/list.jinja')
    def index(self, **kw):
        na_cache = cache.get_cache('tracking.nearest_airport', expire=60 * 60)

        def add_nearest_airport_data(track):
            def get_nearest_airport():
                airport = Airport.by_location(track.location, None)
                if airport is None:
                    return None, None

                distance = airport.distance(track.location)
                return airport, distance

            airport, distance = na_cache.get(key=track.id, createfunc=get_nearest_airport)
            return track, airport, distance

        tracks = []
        tracks.extend(map(add_nearest_airport_data, TrackingFix.get_latest()))

        return dict(tracks=tracks)

    @expose()
    def _lookup(self, id, *remainder):
        pilots = get_requested_record_list(User, id)
        controller = TrackController(pilots)
        return controller, remainder

    @expose('tracking/info.jinja')
    def info(self, **kw):
        user = None
        if request.identity is not None and 'user' in request.identity:
            user = request.identity['user']

        return dict(user=user)

    @expose()
    @jsonp
    def latest(self, **kw):
        if not request.path.endswith('.json'):
            raise HTTPNotFound

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

        return dict(fixes=fixes)
