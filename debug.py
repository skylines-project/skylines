#!/usr/bin/env python

import argparse
from skylines.config import to_envvar

parser = argparse.ArgumentParser(description='Run the SkyLines debug server.')
parser.add_argument('conf_path', nargs='?', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

if not to_envvar(args.conf_path):
    parser.error('Config file "{}" not found.'.format(args.conf_path))

if __name__ == '__main__':
    from skylines import app
    app.add_web_components()
    app.run(port=8080)
