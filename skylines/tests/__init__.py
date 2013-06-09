"""Unit and functional test suite for SkyLines."""

from skylines import db
from skylines.websetup.bootstrap import bootstrap

__all__ = ['setup_db', 'setup_app', 'teardown_db']


def setup_db():
    """Method used to build a database"""
    db.create_all()


def setup_app():
    setup_db()


def teardown_db():
    """Method used to destroy a database"""
    db.session.remove()
    db.drop_all()


def clean_db():
    """Clean all data, leaving schema as is

    Suitable to be run before each db-aware test. This is much faster than
    dropping whole schema an recreating from scratch.
    """
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())

    bootstrap()
    db.session.commit()
