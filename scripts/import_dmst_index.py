#!/usr/bin/python
#
# Parse the DMSt index list from DMSt-WO_2012.pdf
#

import sys
import os
import re
import argparse
import transaction
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment
from skylines.model import DBSession, AircraftModel

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Add or update dmst handicaps in SkyLines.')
parser.add_argument('--config', metavar='config.ini',
                    default='/etc/skylines/production.ini',
                    help='path to the configuration INI file')
parser.add_argument('path', help='DMSt index list file')

args = parser.parse_args()

conf = appconfig('config:' + os.path.abspath(args.config))
load_environment(conf.global_conf, conf.local_conf)

r = re.compile(r'^(.*?)\s*\.+[\.\s]*(\d+)\s*$')

for line in file(args.path):
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
