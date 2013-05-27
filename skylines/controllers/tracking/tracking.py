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
