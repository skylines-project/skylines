# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from math import log
from tg import expose, request
from webob.exc import HTTPNotFound
from sqlalchemy import func
from sqlalchemy.sql.expression import desc
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, TrackingFix
from skylinespolyencode import SkyLinesPolyEncoder


class TrackController(BaseController):
    def __init__(self, pilot):
        self.pilot = pilot

    def __get_flight_path2(self, last_update = None):
        query = DBSession.query(TrackingFix)
        query = query.filter(TrackingFix.pilot == self.pilot)
        query = query.filter(TrackingFix.time >= datetime.now() - timedelta(hours=12))
        query = query.order_by(TrackingFix.time)

        if not query:
            return None

        start_fix = query.first()
        start_time = start_fix.time.hour * 3600 + start_fix.time.minute * 60 + start_fix.time.second

        if last_update:
            query = query.filter(TrackingFix.time >= \
                start_fix.time + timedelta(seconds=(last_update - start_time)))

        result = []
        for fix in query:
            location = fix.location
            if location is None:
                continue

            time_delta = fix.time - start_fix.time
            time = start_time + time_delta.days * 86400 + time_delta.seconds

            result.append((time, location.latitude, location.longitude,
                           fix.altitude))
        return result

    def __get_flight_path(self, threshold = 0.001, last_update = None):
        fp = self.__get_flight_path2(last_update = last_update)
        if len(fp) == 0:
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

        return dict(encoded=encoded, zoom_levels = zoom_levels, fixes = fixes,
                    barogram_t=barogram_t, barogram_h=barogram_h)

    @expose('skylines.templates.tracking.view')
    def index(self):
        return dict(pilot=self.pilot, trace=self.__get_flight_path())

    @expose('skylines.templates.tracking.map')
    def map(self):
        return dict(pilot=self.pilot, trace=self.__get_flight_path())

    @expose('json')
    def json(self, **kw):
        try:
            last_update = int(kw.get('last_update'))
        except ValueError:
            last_update = None

        trace = self.__get_flight_path(threshold=0.001, last_update=last_update)

        return  dict(encoded=trace['encoded'], num_levels=trace['fixes']['numLevels'],
                     barogram_t=trace['barogram_t'], barogram_h=trace['barogram_h'],
                     sfid=self.pilot.user_id)

class TrackingController(BaseController):
    @expose('skylines.templates.tracking.list')
    def index(self, **kw):
        subq = DBSession.query(TrackingFix.pilot_id,
                               func.max(TrackingFix.time).label('time')) \
                .filter(TrackingFix.time >= datetime.now() - timedelta(hours=6)) \
                .group_by(TrackingFix.pilot_id) \
                .subquery()

        query = DBSession.query(subq.c.time, User) \
            .filter(subq.c.pilot_id == User.user_id) \
            .order_by(desc(subq.c.time))

        return dict(tracks=query.all())

    @expose()
    def lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        try:
            user = DBSession.query(User).get(int(id))
        except ValueError:
            raise HTTPNotFound

        if user is None:
            raise HTTPNotFound

        controller = TrackController(user)
        return controller, remainder

    @expose('skylines.templates.tracking.info')
    def info(self):
        user = None
        if request.identity is not None and 'user' in request.identity:
            user = request.identity['user']

        return dict(user=user)
