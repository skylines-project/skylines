#!/usr/bin/env python

import sys
from flask.ext.script import Manager
from skylines import create_combined_app
from config import to_envvar


def create_app(config):
    if not to_envvar(config):
        print 'Config file "{}" not found.'.format(config)
        sys.exit(1)

    return create_combined_app()

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)

if __name__ == "__main__":
    manager.run()
