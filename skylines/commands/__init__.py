import sys

from flask.ext.script import Manager

from .celery import manager as celery_manager
from .tracking import manager as tracking_manager
from .import_srtm import ImportSRTM
from .server import Server
from .shell import Shell

from skylines.app import create_app
from config import to_envvar


def _create_app(config):
    if not to_envvar(config):
        print 'Config file "{}" not found.'.format(config)
        sys.exit(1)

    return create_app()


manager = Manager(_create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command("shell", Shell())
manager.add_command("runserver", Server())
manager.add_command("tracking", tracking_manager)
manager.add_command("celery", celery_manager)
manager.add_command("import-srtm", ImportSRTM())
