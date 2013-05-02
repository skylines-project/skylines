#!/usr/bin/python
#
# Parse the DMSt index list from DMSt-WO_2012.pdf
#

import sys
import os
import argparse
import transaction
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment
from skylines.model import DBSession, Airport
from skylines.lib.waypoints.welt2000 import get_database


sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Add or update welt2000 airport data in SkyLines.')
parser.add_argument('--config', metavar='config.ini',
                    default='/etc/skylines/production.ini',
                    help='path to the configuration INI file')
parser.add_argument('welt2000_path', nargs='?', metavar='WELT2000.TXT',
                    help='path to the WELT2000 file')

args = parser.parse_args()

conf = appconfig('config:' + os.path.abspath(args.config))
load_environment(conf.global_conf, conf.local_conf)

welt2000 = get_database(path=args.welt2000_path)

i = 0

for airport_w2k in welt2000:
    if (airport_w2k.type != 'airport' and
            airport_w2k.type != 'glider_site' and
            airport_w2k.type != 'ulm'):
        continue

    i += 1
    if i % 100 == 0:
        DBSession.flush()
        print str(i) + ": " + airport_w2k.country_code + " " + airport_w2k.name

    airport = Airport()
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

    DBSession.add(airport)

DBSession.flush()

transaction.commit()
