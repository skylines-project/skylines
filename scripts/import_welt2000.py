#!/usr/bin/env python
#
# Parse the DMSt index list from DMSt-WO_2012.pdf
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Add or update welt2000 airport data in SkyLines.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('--commit', action='store_true',
                    help='commit changes. Otherwise no changes are made to the database')
parser.add_argument('welt2000_path', nargs='?', metavar='WELT2000.TXT',
                    help='path to the WELT2000 file')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from skylines import db, app
from skylines.model import Airport
from skylines.lib.waypoints.welt2000 import get_database
from datetime import datetime
from sqlalchemy.sql.expression import or_


def add_airport(airport_w2k):
    airport = Airport()
    update_airport(airport, airport_w2k)
    db.session.add(airport)


def update_airport(airport, airport_w2k):
    airport.location = airport_w2k
    airport.altitude = airport_w2k.altitude

    airport.name = airport_w2k.name
    airport.short_name = airport_w2k.short_name
    airport.icao = airport_w2k.icao
    airport.country_code = airport_w2k.country_code
    airport.surface = airport_w2k.surface
    airport.runway_len = airport_w2k.runway_len
    airport.runway_dir = airport_w2k.runway_dir
    airport.frequency = airport_w2k.freq
    airport.type = airport_w2k.type

    airport.time_modified = current_date


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


def show_differences(airport, airport_w2k):
    row2dict = lambda r: {c.name: getattr(r, c.name) for c in r.__table__.columns}

    diff = DictDiffer(row2dict(airport), airport_w2k.__dict__)

    changed = diff.changed()
    distance = airport.distance(airport_w2k)

    if changed or distance > 0.1:
        print "{}  {}  {}" \
            .format(airport.country_code, airport.name, airport.icao)

        if distance > 0.1:
            print "  moved by {}m".format(distance)

        for item in changed:
            print "  {} from {} to {}" \
                .format(item, row2dict(airport)[item], airport_w2k.__dict__[item])


app.test_request_context().push()

welt2000 = get_database(path=args.welt2000_path)

current_date = datetime.utcnow()
i = 0

for airport_w2k in welt2000:
    if (airport_w2k.type != 'airport' and
            airport_w2k.type != 'glider_site' and
            airport_w2k.type != 'ulm'):
        continue

    i += 1
    if i % 100 == 0:
        db.session.flush()
        print str(i) + ": " + airport_w2k.country_code + " " + airport_w2k.name

    # try to find this airport in the database
    near_airport = Airport.query() \
        .filter(Airport.short_name == airport_w2k.short_name) \
        .filter(or_(Airport.valid_until == None, Airport.valid_until > current_date)) \
        .first()

    # fall back to location-search if airport is not found
    # and only reuse this airport if it's within 250 meters of the old one...
    if near_airport is None or near_airport.distance(airport_w2k) > 250:
        near_airport = Airport.by_location(airport_w2k, distance_threshold=0.0025)

    if near_airport is None:
        # this airport is not in our database yet. add it...
        add_airport(airport_w2k)

    else:
        # seems to be the same airport. update with current values
        show_differences(near_airport, airport_w2k)
        update_airport(near_airport, airport_w2k)

db.session.flush()

# now invalidate all remaining airports

invalid_airports = Airport.query() \
    .filter(Airport.time_modified < current_date) \
    .filter(or_(Airport.valid_until == None, Airport.valid_until > current_date))

for airport in invalid_airports:
    print "{}  {}  {}" \
        .format(airport.country_code, airport.name, airport.icao)
    print "  invalidated"

    airport.valid_until = current_date

if args.commit:
    db.session.commit()
