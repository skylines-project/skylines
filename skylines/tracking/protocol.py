import struct
from skylines.tracking.crc import set_crc


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


def create_ping_message(ping_id):
    message = struct.pack('!IHHQHHI', MAGIC, 0, TYPE_PING,
                          0, ping_id, 0, 0)
    return set_crc(message)


def create_fix_message(
        tracking_key, time, latitude=None, longitude=None,
        track=None, ground_speed=None, airspeed=None, altitude=None,
        vario=None, enl=None):
    """Send a fix packet.

    Keyword arguments:
    tracking_key     int - base16-encoded
    time             milliseconds of day
    latitude         angle in microdegrees
    longitude        angle in microdegrees
    track            track in degrees
    ground_speed     in m/s
    airspeed         in m/s
    altitude         in m
    vario            in m/s
    enl              0-999
    """

    flags = 0

    if latitude is None or longitude is None:
        latitude = 0
        longitude = 0
    else:
        latitude *= 1000000
        longitude *= 1000000
        flags |= FLAG_LOCATION

    if track is None:
        track = 0
    else:
        flags |= FLAG_TRACK

    if ground_speed is None:
        ground_speed = 0
    else:
        ground_speed *= 16
        flags |= FLAG_GROUND_SPEED

    if airspeed is None:
        airspeed = 0
    else:
        airspeed *= 16
        flags |= FLAG_AIRSPEED

    if altitude is None:
        altitude = 0
    else:
        flags |= FLAG_ALTITUDE

    if vario is None:
        vario = 0
    else:
        vario *= 256
        flags |= FLAG_VARIO

    if enl is None:
        enl = 0
    else:
        flags |= FLAG_ENL

    message = struct.pack(
        '!IHHQIIiiIHHHhhH', MAGIC, 0, TYPE_FIX, tracking_key,
        flags, int(time), int(latitude), int(longitude), 0, int(track),
        int(ground_speed), int(airspeed), int(altitude),
        int(vario), int(enl))

    return set_crc(message)
