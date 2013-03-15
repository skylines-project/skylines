import struct
import datetime
from twisted.python import log
from twisted.internet.protocol import DatagramProtocol
from sqlalchemy import distinct
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import and_, or_, desc
import transaction
from skylines.model import DBSession, User, TrackingFix, Location, Follower
from skylines.lib.crc import check_crc, set_crc

# More information about this protocol can be found in the XCSoar
# source code, source file src/Tracking/SkyLines/Protocol.hpp

MAGIC = 0x5df4b67b
TYPE_PING = 1
TYPE_ACK = 2
TYPE_FIX = 3
TYPE_TRAFFIC_REQUEST = 4
TYPE_TRAFFIC_RESPONSE = 5
TYPE_USER_NAME_REQUEST = 6
TYPE_USER_NAME_RESPONSE = 7

FLAG_ACK_BAD_KEY = 0x1

FLAG_LOCATION = 0x1
FLAG_TRACK = 0x2
FLAG_GROUND_SPEED = 0x4
FLAG_AIRSPEED = 0x8
FLAG_ALTITUDE = 0x10
FLAG_VARIO = 0x20
FLAG_ENL = 0x40

# for TYPE_TRAFFIC_REQUEST
TRAFFIC_FLAG_FOLLOWEES = 0x1
TRAFFIC_FLAG_CLUB = 0x2

USER_FLAG_NOT_FOUND = 0x1

class TrackingServer(DatagramProtocol):
    def pingReceived(self, host, port, key, payload):
        if len(payload) != 8: return
        id, reserved, reserved2 = struct.unpack('!HHI', payload)

        flags = 0

        pilot = User.by_tracking_key(key)
        if not pilot:
            flags |= FLAG_ACK_BAD_KEY

        data = struct.pack('!IHHQHHI', MAGIC, 0, TYPE_ACK, 0,
                           id, 0, flags)
        data = set_crc(data)
        self.transport.write(data, (host, port))

    def fixReceived(self, host, key, payload):
        if len(payload) != 32: return
        data = struct.unpack('!IIiiIHHHhhH', payload)

        pilot = User.by_tracking_key(key)
        if not pilot:
            log.err("No such pilot: %x" % key)
            return

        flags = data[0]

        fix = TrackingFix()
        fix.ip = host
        fix.pilot = pilot

        # import the time stamp from the packet if it's within a
        # certain range
        time_of_day_ms = data[1] % (24 * 3600 * 1000)
        time_of_day_s = time_of_day_ms / 1000
        time_of_day = datetime.time(time_of_day_s / 3600,
                                    (time_of_day_s / 60) % 60,
                                    time_of_day_s % 60,
                                    (time_of_day_ms % 1000) * 1000)
        now = datetime.datetime.utcnow()
        now_s = ((now.hour * 60) + now.minute) * 60 + now.second
        if now_s - 1800 < time_of_day_s < now_s + 180:
            fix.time = datetime.datetime.combine(now.date(), time_of_day)
        elif now_s < 1800 and time_of_day_s > 23 * 3600:
            # midnight rollover occurred
            fix.time = datetime.datetime.combine(now.date(), time_of_day) \
                       - datetime.timedelta(days=1)
        else:
            log.msg("ignoring time stamp from FIX packet: " + str(time_of_day))

        if flags & FLAG_LOCATION:
            fix.location = Location(latitude=data[2] / 1000000.,
                                    longitude=data[3] / 1000000.)

        if flags & FLAG_TRACK:
            fix.track = data[5]

        if flags & FLAG_GROUND_SPEED:
            fix.ground_speed = data[6] / 16.

        if flags & FLAG_AIRSPEED:
            fix.airspeed = data[7] / 16.

        if flags & FLAG_ALTITUDE:
            fix.altitude = data[8]

        if flags & FLAG_VARIO:
            fix.vario = data[9] / 256.

        if flags & FLAG_ENL:
            fix.engine_noise_level = data[10]

        log.msg("{} {} {} {}".format(
            fix.time and fix.time.time(), host,
            unicode(pilot).encode('utf8', 'ignore'), fix.location))

        DBSession.add(fix)
        try:
            transaction.commit()
        except SQLAlchemyError, e:
            log.err(e, 'database error')
            transaction.abort()

    def trafficRequestReceived(self, host, port, key, payload):
        if len(payload) != 8: return
        data = struct.unpack('!II', payload)

        pilot = User.by_tracking_key(key)
        if pilot is None:
            log.err("No such pilot: %d" % key)
            return

        flags = data[0]
        or_filters = []

        if flags & TRAFFIC_FLAG_FOLLOWEES:
            subq = DBSession.query(Follower.destination_id) \
                   .filter(Follower.source_id == pilot.id) \
                   .subquery()
            or_filters.append(TrackingFix.pilot_id.in_(subq))

        if flags & TRAFFIC_FLAG_CLUB:
            subq = DBSession.query(User.id) \
                   .filter(User.club_id == pilot.club_id) \
                   .subquery()
            or_filters.append(TrackingFix.pilot_id.in_(subq))

        if len(or_filters) == 0:
            return

        query = DBSession.query(TrackingFix) \
            .distinct(TrackingFix.pilot_id) \
            .filter(and_(TrackingFix.time >= datetime.datetime.utcnow() - datetime.timedelta(hours=2),
                         TrackingFix.pilot_id != pilot.id,
                         TrackingFix.location_wkt != None,
                         TrackingFix.altitude != None,
                         or_(*or_filters))) \
            .order_by(TrackingFix.pilot_id, desc(TrackingFix.time)) \
            .limit(32)

        response = ''
        count = 0
        for fix in query:
            location = fix.location
            if location is None: continue

            t = fix.time
            t = t.hour * 3600000 + t.minute * 60000 + t.second * 1000 + t.microsecond / 1000
            response += struct.pack('!IIiihHI', fix.pilot_id, t,
                                    int(location.latitude * 1000000),
                                    int(location.longitude * 1000000),
                                    int(fix.altitude), 0, 0)
            count += 1

        response = struct.pack('!HBBI', 0, 0, count, 0) + response
        response = struct.pack('!IHHQ', MAGIC, 0, TYPE_TRAFFIC_RESPONSE, 0) + response
        response = set_crc(response)
        self.transport.write(response, (host, port))

    def userNameRequestReceived(self, host, port, key, payload):
        """The client asks for the display name of a user account."""

        if len(payload) != 8: return
        data = struct.unpack('!II', payload)

        pilot = User.by_tracking_key(key)
        if pilot is None:
            log.err("No such pilot: %d" % key)
            return

        user_id = data[0]

        user = DBSession.query(User).get(user_id)
        if user is None:
            response = struct.pack('!IHHQIIIBBBBII', MAGIC, 0, TYPE_USER_NAME_RESPONSE, 0,
                                   user_id, USER_FLAG_NOT_FOUND, 0,
                                   0, 0, 0, 0, 0, 0)
            response = set_crc(response)
            self.transport.write(response, (host, port))
            return

        name = user.display_name[:64].encode('utf8', 'ignore')
        club_id = user.club_id or 0

        response = struct.pack('!IHHQIIIBBBBII', MAGIC, 0, TYPE_USER_NAME_RESPONSE, 0,
                               user_id, 0, club_id,
                               len(name), 0, 0, 0, 0, 0)
        response += name
        response = set_crc(response)
        self.transport.write(response, (host, port))

    def datagramReceived(self, data, (host, port)):
        if len(data) < 16: return

        header = struct.unpack('!IHHQ', data[:16])
        if header[0] != MAGIC: return
        if not check_crc(data): return

        if header[2] == TYPE_FIX:
            self.fixReceived(host, header[3], data[16:])
        elif header[2] == TYPE_PING:
            self.pingReceived(host, port, header[3], data[16:])
        elif header[2] == TYPE_TRAFFIC_REQUEST:
            self.trafficRequestReceived(host, port, header[3], data[16:])
        elif header[2] == TYPE_TRAFFIC_REQUEST:
            self.trafficRequestReceived(host, port, header[3], data[16:])
        elif header[2] == TYPE_USER_NAME_REQUEST:
            self.userNameRequestReceived(host, port, header[3], data[16:])
