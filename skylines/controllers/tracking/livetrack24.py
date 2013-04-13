from datetime import datetime
from tg import request
from webob.exc import HTTPNotFound, HTTPBadRequest, HTTPNotImplemented
from skylines.controllers.base import BaseController
from skylines.model import DBSession, User, TrackingFix, TrackingSession, Location


class LiveTrack24Controller(BaseController):
    def track(self, **kw):
        """
        LiveTrack24 tracking API

        see: http://www.livetrack24.com/wiki/LiveTracking%20API
        """

        # Read and check the request type

        if 'leolive' not in kw:
            raise HTTPBadRequest('`leolive` parameter is missing.')

        try:
            leolive = int(kw['leolive'])
            if not (1 <= leolive <= 4):
                raise ValueError()

        except ValueError:
            raise HTTPBadRequest('`leolive` must be an integer between 1 and 4.')

        if leolive == 1:
            return self.sessionless_fix(**kw)
        elif leolive == 2:
            return self.create_session(**kw)
        elif leolive == 3:
            return self.finish_session(**kw)
        elif leolive == 4:
            return self.session_fix(**kw)

    def client(self, **kw):
        """
        LiveTrack24 tracking API

        see: http://www.livetrack24.com/wiki/LiveTracking%20API
        """

        # Read and check the request type

        if 'op' not in kw:
            raise HTTPBadRequest('`op` parameter is missing.')

        if kw['op'] != 'login':
            raise HTTPBadRequest('`op` parameter has to be `login`.')

        # Read and check the tracking key (supplied via 'user' field)

        key, pilot = self.parse_user(**kw)
        if not pilot:
            return '0'

        return '{:d}'.format(key)

    def sessionless_fix(self, **kw):
        key, pilot = self.parse_user(**kw)
        if not pilot:
            raise HTTPNotFound('No pilot found with tracking key `{:X}`.'.format(key))

        fix = self.parse_fix(pilot.id, **kw)
        DBSession.add(fix)
        return 'OK'

    def session_fix(self, **kw):
        session_id = self.parse_session_id(**kw)
        session = TrackingSession.by_lt24_id(session_id)
        if session is None:
            raise HTTPNotFound('No open tracking session found with id `{d}`.'.format(session_id))

        fix = self.parse_fix(session.pilot_id, **kw)
        DBSession.add(fix)
        return 'OK'

    def create_session(self, **kw):
        key, pilot = self.parse_user(**kw)
        if not pilot:
            raise HTTPNotFound('No pilot found with tracking key `{:X}`.'.format(key))

        session_id = self.parse_session_id(**kw)

        if session_id & 0x00FFFFFF != key & 0x00FFFFFF:
            raise HTTPBadRequest('The right three bytes must match the userid (tracking key).')

        session = TrackingSession()
        session.pilot = pilot
        session.lt24_id = session_id
        session.ip_created = request.remote_addr

        # Client application
        if 'client' in kw:
            session.client = kw['client'][:32]
        if 'v' in kw:
            session.client_version = kw['v'][:8]

        # Device information
        if 'phone' in kw:
            session.device = kw['phone'][:32]
        if 'gps' in kw:
            session.gps_device = kw['gps'][:32]

        # Aircraft model and type
        if 'vname' in kw:
            session.aircraft_model = kw['vname'][:64]
        if 'vtype' in kw:
            try:
                session.aircraft_type = int(kw['vtype'])
            except ValueError:
                raise HTTPBadRequest('`vtype` has to be a valid integer.')

        DBSession.add(session)
        return 'OK'

    def finish_session(self, **kw):
        session_id = self.parse_session_id(**kw)
        session = TrackingSession.by_lt24_id(session_id)
        if session is None:
            raise HTTPNotFound('No open tracking session found with id `{d}`.'.format(session_id))

        session.time_finished = datetime.utcnow()
        session.ip_finished = request.remote_addr

        # Pilot status
        if 'prid' in kw:
            try:
                finish_status = int(kw['prid'])
                if not (0 <= finish_status <= 4):
                    raise ValueError()

                session.finish_status = finish_status

            except ValueError:
                raise HTTPBadRequest('`prid` must be an integer between 0 and 4.')

        DBSession.flush()
        return 'OK'

    def parse_user(self, **kw):
        """Read and check the tracking key (supplied via 'user' field)"""

        if 'user' not in kw:
            raise HTTPBadRequest('`user` parameter is missing.')

        try:
            key = int(kw['user'], 16)
        except ValueError:
            raise HTTPBadRequest('`user` must be the hexadecimal tracking key.')

        return key, User.by_tracking_key(key)

    def parse_session_id(self, **kw):
        """Read and check the session id"""

        if 'sid' not in kw:
            raise HTTPBadRequest('`sid` parameter is missing.')

        try:
            session_id = int(kw['sid'])
        except ValueError:
            raise HTTPBadRequest('`sid` must be an integer.')

        if session_id & 0x80000000 == 0:
            raise HTTPNotImplemented('Unregistered users are not supported.')

        return session_id

    def parse_fix(self, pilot_id, **kw):
        fix = TrackingFix()
        fix.ip = request.remote_addr
        fix.pilot_id = pilot_id

        # Time
        if 'tm' not in kw:
            raise HTTPBadRequest('`tm` (time) parameter is missing.')

        try:
            fix.time = datetime.utcfromtimestamp(int(kw['tm']))
        except ValueError:
            raise HTTPBadRequest('`tm` (time) has to be a POSIX timestamp.')

        # Location
        if 'lat' in kw and 'lon' in kw:
            try:
                fix.set_location(float(kw['lon']), float(kw['lat']))
            except ValueError:
                raise HTTPBadRequest('`lat` and `lon` have to be floating point value in degrees (WGS84).')

        # Altitude
        if 'alt' in kw:
            try:
                fix.altitude = int(kw['alt'])
            except ValueError:
                raise HTTPBadRequest('`alt` has to be an integer value in meters.')

        # Speed
        if 'sog' in kw:
            try:
                fix.ground_speed = int(kw['sog']) / 3.6
            except ValueError:
                raise HTTPBadRequest('`sog` (speed over ground) has to be an integer value in km/h.')

        # Track
        if 'cog' in kw:
            try:
                fix.track = int(kw['cog'])
            except ValueError:
                raise HTTPBadRequest('`cog` (course over ground) has to be an integer value in degrees.')

        return fix
