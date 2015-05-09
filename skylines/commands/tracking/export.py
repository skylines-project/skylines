from flask.ext.script import Command, Option

import hashlib
import aerofiles.igc
from datetime import timedelta
from itertools import chain
from collections import Counter

from skylines.lib import base36
from skylines.database import db
from skylines.model import TrackingFix, User


class Export(Command):
    """ Export live tracks as IGC files """

    option_list = (
        Option('user', type=int, help='a user ID'),
    )

    MANUFACTURER_CODE = 'SKY'

    flights = Counter()

    def run(self, user):
        self.user = User.get(user)

        print 'Generating logger id...',
        m = hashlib.md5()
        m.update(str(user))
        self.logger_id = base36.encode(int(m.hexdigest(), 16))[0:3]
        print self.logger_id

        self.export_sessions(user)

    def get_base_query(self, user_id):
        return db.session.query(TrackingFix) \
            .filter_by(pilot_id=user_id) \
            .order_by(TrackingFix.time)

    def export_sessions(self, user_id):
        fp = None
        writer = None
        last_fix = None
        for fix in chain(self.get_base_query(user_id), [None]):
            is_start = (last_fix is None)
            is_end = (fix is None)

            # check if this is a new live tracking session (dt > 3 hours)
            dt = (fix.time - last_fix.time) if (fix and last_fix) else None
            is_new_session = dt and dt > timedelta(hours=3)

            # update current session
            if not (is_start or is_new_session or is_end):
                self.write_fix(writer, fix)

            # save last_fix in session and append it to the session list
            if last_fix and (is_end or is_new_session):
                if fp:
                    fp.close()

            # start a new session
            if fix and (is_start or is_new_session):
                filename = self.get_filename(fix)
                print 'Writing %s...' % filename

                fp = open(filename, 'w')
                writer = aerofiles.igc.Writer(fp)

                headers = {
                    'manufacturer_code': self.MANUFACTURER_CODE,
                    'logger_id': self.logger_id,
                    'date': fix.time,
                    'pilot': self.user.name,
                    'logger_type': 'SkyLines Live Tracking',
                    'gps_receiver': 'Unknown',
                }

                if self.user.club_id:
                    headers['club'] = self.user.club.name

                writer.write_headers(headers)
                self.write_fix(writer, fix)

            last_fix = fix

    def get_flight_number(self, date):
        key = date.strftime('%Y-%m-%d')
        self.flights[key] += 1
        return self.flights[key]

    def get_filename(self, fix):
        flight_number = self.get_flight_number(fix.time)
        date = fix.time.strftime('%Y-%m-%d')
        filename = '%s-%s-%s-%02d.igc' % (
            date, self.MANUFACTURER_CODE, self.logger_id, flight_number,
        )

        return filename

    def write_fix(self, writer, fix):
        location = fix.location

        f = dict(time=fix.time)
        if location:
            f['latitude'] = location.latitude
            f['longitude'] = location.longitude
            f['valid'] = True

        if fix.altitude is not None:
            f['pressure_alt'] = f['gps_alt'] = fix.altitude

        writer.write_fix(**f)
