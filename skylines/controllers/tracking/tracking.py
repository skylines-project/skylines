from datetime import datetime, timedelta
from tg import expose, request, cache
from webob.exc import HTTPNotFound
from sqlalchemy import func, over
from sqlalchemy.sql.expression import desc, cast
from sqlalchemy.orm import joinedload
from sqlalchemy.types import Interval, String
from skylines.controllers.base import BaseController
from skylines.lib.dbutil import get_requested_record_list
from skylines.lib.helpers import isoformat_utc
from skylines.lib.decorators import jsonp
from skylines.model import DBSession, User, TrackingFix, Airport
from skylines.controllers.tracking import TrackController, \
    LiveTrack24Controller, ExternalTrackingController


class TrackingController(BaseController):
    lt24 = LiveTrack24Controller()
    external = ExternalTrackingController()

    @expose('skylines.templates.tracking.list')
    def index(self, **kw):
        query = self.get_latest_fixes()

        na_cache = cache.get_cache('tracking.nearest_airport', expire=60 * 60)

        tracks = []
        for track in query.all():
            def get_nearest_airport():
                airport = Airport.by_location(track.location, None)
                if airport is None:
                    return None, None

                distance = airport.distance(track.location)
                return airport, distance

            airport, distance = na_cache.get(key=track.id, createfunc=get_nearest_airport)
            tracks.append([track, airport, distance])

        return dict(tracks=tracks)

    @expose()
    def _lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        pilots = get_requested_record_list(User, id)
        controller = TrackController(pilots)
        return controller, remainder

    @expose('skylines.templates.tracking.info')
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
        for fix in self.get_latest_fixes():
            json = dict(time=isoformat_utc(fix.time),
                        location=fix.location_wkt.geom_wkt,
                        pilot=dict(id=fix.pilot_id, name=unicode(fix.pilot)))

            optional_attributes = ['track', 'ground_speed', 'airspeed',
                                   'altitude', 'vario', 'engine_noise_level']
            for attr in optional_attributes:
                value = getattr(fix, attr)
                if value is not None:
                    json[attr] = value

            fixes.append(json)

        return dict(fixes=fixes)

    def get_latest_fixes(self, max_age=timedelta(hours=6), **kw):
        row_number = over(func.row_number(),
                          partition_by=TrackingFix.pilot_id,
                          order_by=desc(TrackingFix.time))

        tracking_delay = cast(cast(User.tracking_delay, String) + ' minutes', Interval)

        subq = DBSession.query(TrackingFix.id,
                               row_number.label('row_number')) \
                .outerjoin(TrackingFix.pilot) \
                .filter(TrackingFix.time >= datetime.utcnow() - max_age) \
                .filter(TrackingFix.time <= datetime.utcnow() - tracking_delay) \
                .filter(TrackingFix.location_wkt != None) \
                .subquery()

        query = DBSession.query(TrackingFix) \
                .options(joinedload(TrackingFix.pilot)) \
                .filter(TrackingFix.id == subq.c.id) \
                .filter(subq.c.row_number == 1) \
                .order_by(desc(TrackingFix.time))

        return query
