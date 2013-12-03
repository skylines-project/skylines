#!/usr/bin/env python

import argparse
from config import to_envvar, DEFAULT_CONF_PATH

parser = argparse.ArgumentParser(description='Run the SkyLines debug server.')
parser.add_argument('conf_path', nargs='?', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

if not to_envvar(args.conf_path):
    parser.error('Config file "{}" not found.'.format(args.conf_path))

if __name__ == '__main__':
    from skylines import create_frontend_app
    app = create_frontend_app()
    app.run(port=8080, extra_files=[DEFAULT_CONF_PATH, args.conf_path or ''])
