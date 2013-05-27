from tg import expose, request, cache
from webob.exc import HTTPNotFound

from . import TrackController
from skylines.controllers.base import BaseController
from skylines.lib.dbutil import get_requested_record_list
from skylines.lib.helpers import isoformat_utc
from skylines.lib.decorators import jsonp
from skylines.model import User, TrackingFix, Airport


class TrackingController(BaseController):
    @expose()
    def _lookup(self, id, *remainder):
        pilots = get_requested_record_list(User, id)
        controller = TrackController(pilots)
        return controller, remainder

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
