#!/usr/bin/env python
#
# Parse the DMSt index list from DMSt-WO_2012.pdf
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Add or update dmst handicaps in SkyLines.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('path', help='DMSt index list file')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


import re
from skylines import db
from skylines.config import environment
from skylines.model import AircraftModel

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
                db.session.add(model)
            model.dmst_index = index

db.session.commit()
