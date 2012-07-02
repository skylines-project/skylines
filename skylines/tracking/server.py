import struct
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import transaction
from skylines.model import DBSession, User, TrackingFix, Location
from skylines.tracking.crc import check_crc, set_crc

# More information about this protocol can be found in the XCSoar
# source code, source file src/Tracking/SkyLines/Protocol.hpp

# this refers to the XCSoar 6.4_alpha1 protocol; delete this when
# alpha1 is deemed obsolete
OLD_MAGIC = 0x5df4b67a
OLD_TYPE_FIX = 1

MAGIC = 0x5df4b67b
TYPE_FIX = 3

FLAG_LOCATION = 0x1
FLAG_TRACK = 0x2
FLAG_GROUND_SPEED = 0x4
FLAG_AIRSPEED = 0x8
FLAG_ALTITUDE = 0x10
FLAG_VARIO = 0x20
FLAG_ENL = 0x40

class TrackingServer(DatagramProtocol):
    def oldFixReceived(self, key, payload):
        """Compatibility with XCSoar 6.4_alpha1.  Remove when XCSoar
        6.4_alpha1 is deemed obsolete."""
        if len(payload) != 32: return
        data = struct.unpack('!QIiiHHHhhH', payload)

        pilot = User.by_tracking_key(key)
        if not pilot:
            print "No such pilot:", key, data
            return

        flags = data[0]

        fix = TrackingFix()
        fix.pilot = pilot

        if flags & FLAG_LOCATION:
            fix.location = Location(latitude=data[2] / 1000000.,
                                    longitude=data[3] / 1000000.)

        if flags & FLAG_TRACK:
            fix.track = data[4]

        if flags & FLAG_GROUND_SPEED:
            fix.ground_speed = data[5] / 16.

        if flags & FLAG_AIRSPEED:
            fix.airspeed = data[6] / 16.

        if flags & FLAG_ALTITUDE:
            fix.altitude = data[7]

        if flags & FLAG_VARIO:
            fix.vario = data[8] / 256.

        if flags & FLAG_ENL:
            fix.engine_noise_level = data[9]

        print pilot, fix.location, data

        DBSession.add(fix)
        DBSession.flush()
        transaction.commit()

    def fixReceived(self, key, payload):
        if len(payload) != 32: return
        data = struct.unpack('!IIIiiHHHhhH', payload)

        pilot = User.by_tracking_key(key)
        if not pilot:
            print "No such pilot:", key, data
            return

        flags = data[0]

        fix = TrackingFix()
        fix.pilot = pilot

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

        print pilot, fix.location, data

        DBSession.add(fix)
        DBSession.flush()
        transaction.commit()

    def datagramReceived(self, data, (host, port)):
        #print "received %r from %s:%d" % (data, host, port)

        if len(data) < 16: return

        header = struct.unpack('!IHHQ', data[:16])
        if header[0] == OLD_MAGIC:
            # Compatibility with XCSoar 6.4_alpha1.  Remove when
            # XCSoar 6.4_alpha1 is deemed obsolete.
            if header[2] == OLD_TYPE_FIX:
                self.oldFixReceived(header[3], data[16:])
            return

        if header[0] != MAGIC: return
        if not check_crc(data): return

        # XXX verify CRC

        if header[2] == TYPE_FIX:
            self.fixReceived(header[3], data[16:])
