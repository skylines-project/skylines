#!/usr/bin/python
#
# Parse the DMSt index list from DMSt-WO_2012.pdf
#

import sys
import os
import re
import transaction
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment
from skylines.model import DBSession, AircraftModel

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = '/etc/skylines/production.ini'
if len(sys.argv) > 2:
    conf_path = sys.argv[1]
    del sys.argv[1]

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %s [config.ini] PATH" % sys.argv[0]
    sys.exit(1)

conf = appconfig('config:' + os.path.abspath(conf_path))
load_environment(conf.global_conf, conf.local_conf)

path = sys.argv[1]

r = re.compile(r'^(.*?)\s*\.+[\.\s]*(\d+)\s*$')

for line in file(path):
    m = r.match(line)
    if m:
        names, index = m.group(1), int(m.group(2))
        for name in names.split(';'):
            name = name.strip().decode('utf-8')
            model = AircraftModel.by_name(name)
            if model is None:
                model = AircraftModel(name=name)
                model.kind = 1
                DBSession.add(model)
            model.dmst_index = index

DBSession.flush()
transaction.commit()
