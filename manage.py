#!/usr/bin/env python

import sys

from flask import current_app
from flask.ext.script import Manager, Shell

from skylines.app import create_app
from skylines import model
from skylines.commands import (
    tracking_manager, celery_manager, ImportSRTM, Server
)
from config import to_envvar


def _create_app(config):
    if not to_envvar(config):
        print 'Config file "{}" not found.'.format(config)
        sys.exit(1)

    return create_app()


def _make_context():
    return dict(app=current_app, model=model, db=model.db)


manager = Manager(_create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command("shell", Shell(make_context=_make_context))
manager.add_command("runserver", Server())
manager.add_command("tracking", tracking_manager)
manager.add_command("celery", celery_manager)
manager.add_command("import-srtm", ImportSRTM())

if __name__ == "__main__":
    manager.run()
