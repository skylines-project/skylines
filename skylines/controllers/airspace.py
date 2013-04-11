from tg import expose, redirect
from tg.decorators import paginate, without_trailing_slash
from webob.exc import HTTPBadRequest
from skylines.controllers.base import BaseController
from skylines.model import DBSession, Airspace
from skylines.model.geo import Location

__all__ = ['AirspaceController']


class AirspaceController(BaseController):
    @expose('json')
    def info(self, **kwargs):
        try:
            latitude = float(kwargs['lat'])
            longitude = float(kwargs['lon'])

        except (KeyError, ValueError):
            raise HTTPBadRequest

        location = Location(latitude=latitude,
                            longitude=longitude)

        airspaces = Airspace.get_info(location)
        info = []

        for airspace in airspaces:
            info.append(dict(name=airspace.name,
                             base=airspace.base,
                             top=airspace.top,
                             airspace_class=airspace.airspace_class,
                             country=airspace.country_code))

        return dict(airspaces=info)
