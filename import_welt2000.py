#!/usr/bin/python
#
# Parse the DMSt index list from DMSt-WO_2012.pdf
#

import sys, os, re
import transaction
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment
from skylines.model import DBSession, Location, Airport
from skylines.lib.waypoints.welt2000 import get_database

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = '/etc/skylines/production.ini'
if len(sys.argv) > 1:
    conf_path = sys.argv[1]
    del sys.argv[1]

if len(sys.argv) != 1:
    print >>sys.stderr, "Usage: %s [config.ini]" % sys.argv[0]
    sys.exit(1)

conf = appconfig('config:' + os.path.abspath(conf_path))
load_environment(conf.global_conf, conf.local_conf)

welt2000 = get_database()

i = 0

for airport_w2k in welt2000:
    if airport_w2k.type != 'airport' \
        and airport_w2k.type != 'glider_site' \
        and airport_w2k.type != 'uml':
      continue

    i += 1
    if i%100 == 0:
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

