from __future__ import print_function

import sys

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from .shell import Shell
from .server import Server, APIServer

from .aircraft import manager as aircraft_manager
from .celery import manager as celery_manager
from .database import manager as database_manager
from .flights import manager as flights_manager
from .import_ import manager as import_manager
from .notifications import manager as notifications_manager
from .tracking import manager as tracking_manager
from .users import manager as users_manager

from .search import Search

from skylines.app import create_app
from skylines.database import db
from config import to_envvar


def _create_app(config):
    if not to_envvar(config):
        print('Config file "{}" not found.'.format(config))
        sys.exit(1)

    app = create_app()
    app.migrate = Migrate(app, db)
    return app


manager = Manager(_create_app)

manager.add_option("-c", "--config", dest="config", required=False)
manager.add_command("shell", Shell())
manager.add_command("runserver", Server(host="0.0.0.0"))
manager.add_command("run_api_server", APIServer(host="0.0.0.0", port=5001))
manager.add_command("migrate", MigrateCommand)

manager.add_command("aircraft", aircraft_manager)
manager.add_command("celery", celery_manager)
manager.add_command("db", database_manager)
manager.add_command("flights", flights_manager)
manager.add_command("import", import_manager)
manager.add_command("notifications", notifications_manager)
manager.add_command("tracking", tracking_manager)
manager.add_command("users", users_manager)

manager.add_command("search", Search())
