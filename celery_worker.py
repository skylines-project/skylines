#!/usr/bin/env python
#
# The Celery worker daemon, which runs asyncronous tasks for SkyLines
#

import argparse
from config import to_envvar

parser = argparse.ArgumentParser(description='Run the Celery worker daemon.')
parser.add_argument('--config', nargs='?', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

if __name__ == '__main__':
    from skylines import create_app
    from skylines.worker.celery import celery

    celery.init_app(create_app())
    celery.worker_main()
