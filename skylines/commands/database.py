from flask.ext.script import Manager

from skylines.model import db
from alembic.config import Config
from alembic import command

manager = Manager(help="Perform operations related to the database")


@manager.command
def init():
    """ Initialize the database by creating the necessary tables and indices """

    # create all tables and indices
    db.create_all()

    # create alembic version table
    alembic_cfg = Config("alembic.ini")
    command.stamp(alembic_cfg, "head")
