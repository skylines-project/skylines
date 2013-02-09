from datetime import datetime
from tg import request, expose
from webob.exc import HTTPNotFound, HTTPBadRequest, HTTPCreated
from skylines.controllers.base import BaseController
from skylines.model import DBSession, User, ExternalTrackingFix, Location


class ExternalTrackingController(BaseController):
    @expose()
    def add(self, **kw):
        # Read and check the owner via tracking key

        key, owner = self.parse_key(**kw)
        if not owner:
            raise HTTPNotFound('No user account found with tracking key `{:X}`.'.format(key))

        # Read and check the tracking type

        if 'type' not in kw:
            raise HTTPBadRequest('`type` parameter is missing.')

        try:
            tracking_type = int(kw['type'])
            if not (0 <= tracking_type <= 1):
                raise ValueError()

        except ValueError:
            raise HTTPBadRequest('`type` must be an integer between 0 and 1.')

        # Read the tracking id

        if 'id' not in kw:
            raise HTTPBadRequest('`id` parameter is missing.')

        try:
            tracking_id = int(kw['id'], 16)
        except ValueError:
            raise HTTPBadRequest('`id` must be an hexadecimal tracking id (e.g. Flarm ID).')

        # Read the fix data

        fix = self.parse_fix(**kw)

        if 'actype' in kw:
            try:
                aircraft_type = int(kw['actype'])
                if not (0 <= aircraft_type <= 15):
                    raise ValueError()

                fix.aircraft_type = aircraft_type

            except ValueError:
                raise HTTPBadRequest('`actype` must be an integer between 0 and 15.')

        # Add meta data to ExternalTrackingFix instance

        fix.tracking_type = tracking_type
        fix.tracking_id = tracking_id
        fix.owner_id = owner.id
        fix.ip = request.remote_addr

        # Add the fix to the database
        DBSession.add(fix)

        return HTTPCreated()

    def parse_key(self, **kw):
        """Read and check the tracking key"""

        if 'key' not in kw:
            raise HTTPBadRequest('`key` parameter is missing.')

        try:
            key = int(kw['key'], 16)
        except ValueError:
            raise HTTPBadRequest('`key` must be the hexadecimal tracking key.')

        return key, User.by_tracking_key(key)

    def parse_fix(self, **kw):
        fix = ExternalTrackingFix()

        # Time
        if 'time' not in kw:
            raise HTTPBadRequest('`time` parameter is missing.')

        try:
            fix.time = datetime.utcfromtimestamp(int(kw['time']))
        except ValueError:
            raise HTTPBadRequest('`time` has to be a POSIX timestamp.')

        # Location
        if 'lat' in kw and 'lon' in kw:
            try:
                fix.location = Location(latitude=float(kw['lat']),
                                        longitude=float(kw['lon']))
            except ValueError:
                raise HTTPBadRequest('`lat` and `lon` have to be floating point value in degrees (WGS84).')

        # Altitude
        if 'alt' in kw:
            try:
                fix.altitude = int(kw['alt'])
            except ValueError:
                raise HTTPBadRequest('`alt` has to be an integer value in meters.')

        # Ground Speed
        if 'speed' in kw:
            try:
                fix.ground_speed = float(kw['speed'])
            except ValueError:
                raise HTTPBadRequest('`speed` has to be a floating point value in m/s.')

        # Track
        if 'track' in kw:
            try:
                fix.track = int(kw['track'])
            except ValueError:
                raise HTTPBadRequest('`track` has to be an integer value in degrees.')

        # Vario
        if 'vario' in kw:
            try:
                fix.vario = float(kw['vario'])
            except ValueError:
                raise HTTPBadRequest('`vario` has to be a floating point  value in m/s.')

        return fix
