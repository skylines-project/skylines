from flask_script import Manager, prompt_bool
from flask_migrate import stamp

from skylines.database import db

manager = Manager(help="Perform database operations")


@manager.command
def create():
    """ Initialize the database by creating the necessary tables and indices """

    # create all tables and indices
    db.create_all()

    # create alembic version table
    stamp()


@manager.command
def drop():
    """ Drops database tables """

    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@manager.command
def bootstrap():
    """ Bootstrap the database with some initial data """

    from tests.data.bootstrap import bootstrap as _bootstrap

    _bootstrap()
