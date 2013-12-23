import pytest
from unittest import TestCase
from mock import Mock, patch

from skylines.model import db, TrackingFix

import struct
from skylines.tracking import server
from skylines.tracking.crc import set_crc, check_crc
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError


@pytest.mark.usefixtures("bootstraped_db")
class TrackingServerTest(TestCase):
    HOST_PORT = ('127.0.0.1', 5597)

    def setUp(self):
        server.TrackingServer.__init__ = Mock(return_value=None)
        self.server = server.TrackingServer()

    def tearDown(self):
        # Clear the database
        TrackingFix.query().delete()

    def test_ping(self):
        """ Tracking server sends ACK when PING is received """

        # Create fake ping message
        ping_id = 42
        message = struct.pack('!IHHQHHI', server.MAGIC, 0, server.TYPE_PING,
                              0, ping_id, 0, 0)
        message = set_crc(message)

        # Create mockup function
        def check_pong(data, host_port):
            # Make sure the host and port match up
            assert host_port == self.HOST_PORT

            # Check if this is a valid message
            assert len(data) >= 16

            header = struct.unpack('!IHHQ', data[:16])
            assert header[0] == server.MAGIC
            assert check_crc(data)

            assert header[2] == server.TYPE_ACK

            ping_id2, _, flags = struct.unpack('!HHI', data[16:])
            assert ping_id2 == ping_id
            assert flags & server.FLAG_ACK_BAD_KEY

        # Connect mockup function to tracking server
        self.server.transport = Mock()
        self.server.transport.write = Mock(side_effect=check_pong)

        # Send fake ping message
        self.server.datagramReceived(message, self.HOST_PORT)

        # Check that mockup function was called
        assert self.server.transport.write.called

    def test_ping_with_key(self):
        """ Tracking server can query by tracking key """

        # Create fake ping message
        ping_id = 42
        message = struct.pack('!IHHQHHI', server.MAGIC, 0, server.TYPE_PING,
                              123456, ping_id, 0, 0)
        message = set_crc(message)

        # Create mockup function
        def check_pong(data, host_port):
            # Make sure the host and port match up
            assert host_port == self.HOST_PORT

            # Check if this is a valid message
            assert len(data) >= 16

            header = struct.unpack('!IHHQ', data[:16])
            assert header[0] == server.MAGIC
            assert check_crc(data)

            assert header[2] == server.TYPE_ACK

            ping_id2, _, flags = struct.unpack('!HHI', data[16:])
            assert ping_id2 == ping_id
            assert not (flags & server.FLAG_ACK_BAD_KEY)

        # Connect mockup function to tracking server
        self.server.transport = Mock()
        self.server.transport.write = Mock(side_effect=check_pong)

        # Send fake ping message
        self.server.datagramReceived(message, self.HOST_PORT)

        # Check that mockup function was called
        assert self.server.transport.write.called

    def create_fix_message(
            self, tracking_key, time, latitude=None, longitude=None,
            track=None, ground_speed=None, airspeed=None, altitude=None,
            vario=None, enl=None):

        flags = 0

        if latitude is None or longitude is None:
            latitude = 0
            longitude = 0
        else:
            latitude *= 1000000
            longitude *= 1000000
            flags |= server.FLAG_LOCATION

        if track is None:
            track = 0
        else:
            flags |= server.FLAG_TRACK

        if ground_speed is None:
            ground_speed = 0
        else:
            ground_speed *= 16
            flags |= server.FLAG_GROUND_SPEED

        if airspeed is None:
            airspeed = 0
        else:
            airspeed *= 16
            flags |= server.FLAG_AIRSPEED

        if altitude is None:
            altitude = 0
        else:
            flags |= server.FLAG_ALTITUDE

        if vario is None:
            vario = 0
        else:
            vario *= 256
            flags |= server.FLAG_VARIO

        if enl is None:
            enl = 0
        else:
            flags |= server.FLAG_ENL

        message = struct.pack(
            '!IHHQIIiiIHHHhhH', server.MAGIC, 0, server.TYPE_FIX, tracking_key,
            flags, int(time), int(latitude), int(longitude), 0, int(track),
            int(ground_speed), int(airspeed), int(altitude),
            int(vario), int(enl))

        return set_crc(message)

    def test_empty_tracking_key(self):
        """ Tracking server declines fixes without tracking key """

        # Create fake fix message
        message = self.create_fix_message(0, 0)

        # Send fake ping message
        self.server.datagramReceived(message, self.HOST_PORT)

        # Check if the message was properly received
        assert TrackingFix.query().count() == 0

    def test_empty_fix(self):
        """ Tracking server accepts empty fixes """

        # Create fake fix message
        message = self.create_fix_message(123456, 0)

        utcnow_return_value = datetime(year=2005, month=4, day=13)
        with patch('skylines.tracking.server.datetime') as datetime_mock:
            datetime_mock.combine.side_effect = \
                lambda *args, **kw: datetime.combine(*args, **kw)

            # Connect utcnow mockup
            datetime_mock.utcnow.return_value = utcnow_return_value

            # Send fake ping message
            self.server.datagramReceived(message, self.HOST_PORT)

        # Check if the message was properly received and written to the database
        fixes = TrackingFix.query().all()

        assert len(fixes) == 1

        fix = fixes[0]
        assert fix.ip == self.HOST_PORT[0]

        assert fix.time == utcnow_return_value
        assert fix.location_wkt == None
        assert fix.track == None
        assert fix.ground_speed == None
        assert fix.airspeed == None
        assert fix.altitude == None
        assert fix.vario == None
        assert fix.engine_noise_level == None

    def test_real_fix(self):
        """ Tracking server accepts real fixes """

        utcnow_return_value = datetime(year=2013, month=1, day=1,
                                       hour=12, minute=34, second=56)

        # Create fake fix message
        now = utcnow_return_value
        now_s = ((now.hour * 60) + now.minute) * 60 + now.second
        message = self.create_fix_message(
            123456, now_s * 1000, latitude=52.7, longitude=7.52,
            track=234, ground_speed=33.25, airspeed=32., altitude=1234,
            vario=2.25, enl=10)

        with patch('skylines.tracking.server.datetime') as datetime_mock:
            datetime_mock.combine.side_effect = \
                lambda *args, **kw: datetime.combine(*args, **kw)

            # Connect utcnow mockup
            datetime_mock.utcnow.return_value = utcnow_return_value

            # Send fake ping message
            self.server.datagramReceived(message, self.HOST_PORT)

        # Check if the message was properly received and written to the database
        fixes = TrackingFix.query().all()

        assert len(fixes) == 1

        fix = fixes[0]
        assert fix.ip == self.HOST_PORT[0]

        assert fix.time == utcnow_return_value
        assert fix.location.to_wkt() == 'POINT(7.52 52.7)'
        assert fix.track == 234
        assert fix.ground_speed == 33.25
        assert fix.airspeed == 32.
        assert fix.altitude == 1234
        assert fix.vario == 2.25
        assert fix.engine_noise_level == 10

    def test_failing_fix(self):
        """ Tracking server handles SQLAlchemyError gracefully """

        # Mock the transaction commit to fail
        commitmock = Mock(side_effect=SQLAlchemyError())
        with patch.object(db.session, 'commit', commitmock):
            # Create fake fix message
            message = self.create_fix_message(123456, 0)

            # Send fake ping message
            self.server.datagramReceived(message, self.HOST_PORT)

        # Check if the message was properly received
        assert TrackingFix.query().count() == 0
        assert commitmock.called

if __name__ == "__main__":
    pytest.main(__file__)
