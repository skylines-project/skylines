from datetime import datetime, timedelta
from math import log
from tg import expose, request
from tg.decorators import with_trailing_slash
from webob.exc import HTTPNotFound
from sqlalchemy.sql.expression import and_
from skylines.controllers.base import BaseController
from skylines.model import DBSession, TrackingFix
from skylinespolyencode import SkyLinesPolyEncoder


def get_flight_path2(pilot, last_update=None):
    query = DBSession.query(TrackingFix)
    query = query.filter(and_(TrackingFix.pilot == pilot,
                              TrackingFix.location != None,
                              TrackingFix.altitude != None,
                              TrackingFix.time >= datetime.utcnow() - timedelta(hours=12)))
    if pilot.tracking_delay > 0 and not pilot.is_readable(request.identity):
        query = query.filter(TrackingFix.time <= datetime.utcnow() - timedelta(minutes=pilot.tracking_delay))
    query = query.order_by(TrackingFix.time)

    start_fix = query.first()

    if not start_fix:
        return None

    start_time = start_fix.time.hour * 3600 + start_fix.time.minute * 60 + start_fix.time.second

    if last_update:
        query = query.filter(TrackingFix.time >= start_fix.time +
                             timedelta(seconds=(last_update - start_time)))

    result = []
    for fix in query:
        location = fix.location
        if location is None:
            continue

        time_delta = fix.time - start_fix.time
        time = start_time + time_delta.days * 86400 + time_delta.seconds

        result.append((time, location.latitude, location.longitude,
                       fix.altitude, fix.engine_noise_level))
    return result


def get_flight_path(pilot, threshold=0.001, last_update=None):
    fp = get_flight_path2(pilot, last_update=last_update)
    if fp is None or len(fp) == 0:
        return None

    num_levels = 4
    zoom_factor = 4
    zoom_levels = [0]
    zoom_levels.extend([round(-log(32.0 / 45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2)) for i in range(1, num_levels)])

    encoder = SkyLinesPolyEncoder(num_levels=4, threshold=threshold, zoom_factor=4)
    fixes = dict()

    if len(fp) == 1:
        x = fp[0]
        fixes['points'] = [(x[2], x[1])]
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

    return dict(encoded=encoded, zoom_levels=zoom_levels, fixes=fixes,
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

    @with_trailing_slash
    @expose('tracking/view.jinja')
    def index(self):
        other_pilots = []
        for pilot in self.other_pilots:
            trace = get_flight_path(pilot)
            if trace is not None:
                other_pilots.append((pilot, trace))

        return dict(pilot=self.pilot, trace=self.__get_flight_path(),
                    other_pilots=other_pilots)

    @expose('tracking/map.jinja')
    def map(self):
        other_pilots = []
        for pilot in self.other_pilots:
            trace = get_flight_path(pilot)
            if trace is not None:
                other_pilots.append((pilot, trace))

        return dict(pilot=self.pilot, trace=self.__get_flight_path(),
                    other_pilots=other_pilots)

    @expose('json')
    def json(self, **kw):
        try:
            last_update = int(kw.get('last_update', 0))
        except ValueError:
            last_update = None

        trace = self.__get_flight_path(threshold=0.001, last_update=last_update)
        if trace is None:
            raise HTTPNotFound

        return dict(encoded=trace['encoded'], num_levels=trace['fixes']['numLevels'],
                    barogram_t=trace['barogram_t'], barogram_h=trace['barogram_h'],
                    enl=trace['enl'], sfid=self.pilot.id)
