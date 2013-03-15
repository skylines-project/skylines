from unittest import TestCase
from nose.tools import eq_, ok_
from mock import Mock

import transaction
from skylines.model.session import DBSession
from skylines.tests import setup_app, teardown_db

import struct
from skylines.tracking import server
from skylines.lib.crc import set_crc, check_crc


def setup():
    # Setup the database
    DBSession.remove()
    transaction.begin()
    setup_app()


def teardown():
    # Remove the database again
    DBSession.rollback()
    teardown_db()


class TrackingServerTest(TestCase):
    HOST_PORT = ('localhost', 5597)

    def setUp(self):
        server.TrackingServer.__init__ = Mock(return_value=None)
        self.server = server.TrackingServer()

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
            eq_(host_port, self.HOST_PORT)

            # Check if this is a valid message
            assert len(data) >= 16

            header = struct.unpack('!IHHQ', data[:16])
            eq_(header[0], server.MAGIC)
            ok_(check_crc(data))

            eq_(header[2], server.TYPE_ACK)

            ping_id2, _, flags = struct.unpack('!HHI', data[16:])
            eq_(ping_id2, ping_id)
            ok_(flags & server.FLAG_ACK_BAD_KEY)

        # Connect mockup function to tracking server
        self.server.transport = Mock()
        self.server.transport.write = Mock(side_effect=check_pong)

        # Send fake ping message
        self.server.datagramReceived(message, self.HOST_PORT)

        # Check that mockup function was called
        ok_(self.server.transport.write.called)

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
            eq_(host_port, self.HOST_PORT)

            # Check if this is a valid message
            assert len(data) >= 16

            header = struct.unpack('!IHHQ', data[:16])
            eq_(header[0], server.MAGIC)
            ok_(check_crc(data))

            eq_(header[2], server.TYPE_ACK)

            ping_id2, _, flags = struct.unpack('!HHI', data[16:])
            eq_(ping_id2, ping_id)
            ok_(not (flags & server.FLAG_ACK_BAD_KEY))

        # Connect mockup function to tracking server
        self.server.transport = Mock()
        self.server.transport.write = Mock(side_effect=check_pong)

        # Send fake ping message
        self.server.datagramReceived(message, self.HOST_PORT)

        # Check that mockup function was called
        ok_(self.server.transport.write.called)


if __name__ == "__main__":
    import sys
    import nose

    sys.argv.append(__name__)
    nose.run()
