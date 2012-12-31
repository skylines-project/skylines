#!/usr/bin/python
#
# The SkyLines daemon, responsible for live tracking (and maybe other
# Twisted applications).
#

import sys
import os
import argparse
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment
from skylines.tracking import Server

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Run the SkyLines Live Tracking daemon.')
parser.add_argument('conf_path', nargs='?', metavar='config.ini',
                    default='/etc/skylines/production.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

conf = appconfig('config:' + os.path.abspath(args.conf_path))
load_environment(conf.global_conf, conf.local_conf)

if __name__ == '__main__':
    Server().run()
