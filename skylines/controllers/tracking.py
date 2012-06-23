# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from math import log
from tg import expose
from webob.exc import HTTPNotFound
from sqlalchemy import func
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import DBSession, User, TrackingFix
from skylinespolyencode import SkyLinesPolyEncoder
from skylines.lib.analysis import flight_path

class TrackController(BaseController):
    def __init__(self, pilot):
        self.pilot = pilot

    def __get_flight_path2(self):
        query = DBSession.query(TrackingFix)
        query = query.filter(TrackingFix.time >= datetime.now() - timedelta(hours=12))
        query = query.order_by(TrackingFix.time)

        result = []
        for fix in query:
            # TODO: handle midnight wraparound
            result.append((fix.time.hour * 3600 + fix.time.minute * 60 + fix.time.second,
                           fix.latitude, fix.longitude,
                           fix.altitude))
        return result

    def __get_flight_path(self, threshold = 0.001):
        fp = self.__get_flight_path2()

        num_levels = 4
        zoom_factor = 4
        zoom_levels = [0]
        zoom_levels.extend([round(-log(32.0/45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2)) for i in range(1, num_levels)])

        max_delta_time = max(4, (fp[-1][0] - fp[0][0]) / 500)

        encoder = SkyLinesPolyEncoder(num_levels=4, threshold=threshold, zoom_factor=4)

        fixes = map(lambda x: (x[2], x[1], (x[0]/max_delta_time*threshold)), fp)
        fixes = encoder.classify(fixes, remove=False, type="ppd")

        encoded = encoder.encode(fixes['points'], fixes['levels'])

        barogram_t = encoder.encodeList([fp[i][0] for i in range(len(fp)) if fixes['levels'][i] != -1])
        barogram_h = encoder.encodeList([fp[i][3] for i in range(len(fp)) if fixes['levels'][i] != -1])

        return dict(encoded=encoded, zoom_levels = zoom_levels, fixes = fixes,
                    barogram_t=barogram_t, barogram_h=barogram_h, sfid=self.pilot.user_id)

    @expose('skylines.templates.tracking.view')
    def index(self):
        return dict(pilot=self.pilot, trace=self.__get_flight_path())

class TrackIdController(BaseController):
    @expose()
    def lookup(self, id, *remainder):
        user = DBSession.query(User).get(int(id))
        if user is None:
            raise HTTPNotFound

        controller = TrackController(user)
        return controller, remainder

class TrackingController(BaseController):
    @expose('skylines.templates.tracking.list')
    def index(self, **kw):
        query = DBSession.query(func.max(TrackingFix.time), TrackingFix.pilot_id)
        query = query.filter(TrackingFix.time >= datetime.now() - timedelta(hours=2))
        query = query.group_by(TrackingFix.pilot_id)

        return dict(tracks=query.all())

    id = TrackIdController()
