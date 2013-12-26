from flask.ext.script import Manager, prompt_bool

from skylines.model import db
from alembic.config import Config
from alembic import command
from tests.data.bootstrap import bootstrap as _bootstrap

manager = Manager(help="Perform database operations")


@manager.command
def create():
    """ Initialize the database by creating the necessary tables and indices """

    # create all tables and indices
    db.create_all()

    # create alembic version table
    alembic_cfg = Config("alembic.ini")
    command.stamp(alembic_cfg, "head")


@manager.command
def drop():
    """ Drops database tables """

    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@manager.command
def bootstrap():
    """ Bootstrap the database with some initial data """

    _bootstrap()
