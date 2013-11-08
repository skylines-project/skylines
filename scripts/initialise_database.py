#!/usr/bin/env python
#
# Initialize the database by creating the necessary tables and indices.
#

import argparse
from config import to_envvar

# Parse command line parameters
parser = argparse.ArgumentParser(
    description='Initialize the database by creating the necessary tables and indices.')

parser.add_argument('config', nargs='?', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


# import db instance and the model to register the model metadata

from skylines import db, model  # noqa

# create all tables and indices

db.create_all()

# create alembic version table

from alembic.config import Config
from alembic import command
alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")
