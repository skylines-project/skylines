# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from math import log
from tg import expose, request
from webob.exc import HTTPNotFound
from sqlalchemy import func, over
from sqlalchemy.sql.expression import and_, desc
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, TrackingFix, Airport
from skylinespolyencode import SkyLinesPolyEncoder


def get_flight_path2(pilot, last_update = None):
    query = DBSession.query(TrackingFix)
    query = query.filter(and_(TrackingFix.pilot == pilot,
                              TrackingFix.location != None,
                              TrackingFix.altitude != None,
                              TrackingFix.time >= datetime.now() - timedelta(hours=12)))
    query = query.order_by(TrackingFix.time)

    start_fix = query.first()

    if not start_fix:
        return None

    start_time = start_fix.time.hour * 3600 + start_fix.time.minute * 60 + start_fix.time.second

    if last_update:
        query = query.filter(TrackingFix.time >= \
            start_fix.time + timedelta(seconds=(last_update - start_time)))

    result = []
    for fix in query:
        location = fix.location

        time_delta = fix.time - start_fix.time
        time = start_time + time_delta.days * 86400 + time_delta.seconds

        result.append((time, location.latitude, location.longitude,
                       fix.altitude, fix.engine_noise_level))
    return result


def get_flight_path(pilot, threshold = 0.001, last_update = None):
    fp = get_flight_path2(pilot, last_update = last_update)
    if fp is None or len(fp) == 0:
        raise HTTPNotFound

    num_levels = 4
    zoom_factor = 4
    zoom_levels = [0]
    zoom_levels.extend([round(-log(32.0 / 45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2)) for i in range(1, num_levels)])

    encoder = SkyLinesPolyEncoder(num_levels=4, threshold=threshold, zoom_factor=4)
    fixes = dict()

    if len(fp) == 1:
        fixes['points'] = [(fp[0][0], fp[0][1])]
        fixes['levels'] = [0]
        fixes['numLevels'] = num_levels

    else:
        max_delta_time = max(4, (fp[-1][0] - fp[0][0]) / 500)

        fixes = map(lambda x: (x[2], x[1], (x[0] / max_delta_time * threshold)), fp)
        fixes = encoder.classify(fixes, remove=False, type="ppd")

    encoded = encoder.encode(fixes['points'], fixes['levels'])

    barogram_t = encoder.encodeList([fp[i][0] for i in range(len(fp)) if fixes['levels'][i] != -1])
    barogram_h = encoder.encodeList([fp[i][3] for i in range(len(fp)) if fixes['levels'][i] != -1])
    enl = encoder.encodeList([fp[i][4] or 0 for i in range(len(fp)) if fixes['levels'][i] != -1])

    return dict(encoded=encoded, zoom_levels = zoom_levels, fixes = fixes,
                barogram_t=barogram_t, barogram_h=barogram_h, enl=enl)


class TrackController(BaseController):
    def __init__(self, pilot):
        if isinstance(pilot, list):
            self.pilot = pilot[0]
            self.other_pilots = pilot[1:]
        else:
            self.pilot = pilot
            self.other_pilots = None

    def __get_flight_path(self, **kw):
        return get_flight_path(self.pilot, **kw)

    @expose('skylines.templates.tracking.view')
    def index(self):
        def add_flight_path(pilot):
            trace = get_flight_path(pilot)
            return (pilot, trace)

        other_pilots = map(add_flight_path, self.other_pilots)
        return dict(pilot=self.pilot, trace=self.__get_flight_path(),
                    other_pilots=other_pilots)

    @expose('skylines.templates.tracking.map')
    def map(self):
        def add_flight_path(pilot):
            trace = get_flight_path(pilot)
            return (pilot, trace)

        other_pilots = map(add_flight_path, self.other_pilots)
        return dict(pilot=self.pilot, trace=self.__get_flight_path(),
                    other_pilots=other_pilots)

    @expose('json')
    def json(self, **kw):
        try:
            last_update = int(kw.get('last_update', 0))
        except ValueError:
            last_update = None

        trace = self.__get_flight_path(threshold=0.001, last_update=last_update)

        return  dict(encoded=trace['encoded'], num_levels=trace['fixes']['numLevels'],
                     barogram_t=trace['barogram_t'], barogram_h=trace['barogram_h'],
                     enl=trace['enl'], sfid=self.pilot.user_id)


class TrackingController(BaseController):
    @expose('skylines.templates.tracking.list')
    def index(self, **kw):
        subq = DBSession.query(TrackingFix,
                               over(func.rank(),
                                    partition_by=TrackingFix.pilot_id,
                                    order_by=desc(TrackingFix.time)).label('rank')) \
                .outerjoin(TrackingFix.pilot) \
                .filter(TrackingFix.time >= datetime.now() - timedelta(hours=6)) \
                .filter(TrackingFix.location_wkt != None) \
                .subquery()

        query = DBSession.query(TrackingFix) \
                .filter(TrackingFix.id == subq.c.id) \
                .filter(subq.c.rank == 1) \
                .order_by(desc(TrackingFix.time))

        tracks = []
        for track in query.all():
            airport = Airport.by_location(track.location, None)
            distance = airport.distance(track.location)
            tracks.append([track, airport, distance])

        return dict(tracks=tracks)

    @expose()
    def lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        def get_pilot_by_id_string(id_string):
            try:
                id = int(id_string)
            except ValueError:
                raise HTTPNotFound
            user = DBSession.query(User).get(id)
            if user is None:
                raise HTTPNotFound
            return user

        ids = list()
        for unique_id in id.split(','):
            if unique_id not in ids:
                ids.append(unique_id)

        controller = TrackController(map(get_pilot_by_id_string, ids))
        return controller, remainder

    @expose('skylines.templates.tracking.info')
    def info(self):
        user = None
        if request.identity is not None and 'user' in request.identity:
            user = request.identity['user']

        return dict(user=user)
