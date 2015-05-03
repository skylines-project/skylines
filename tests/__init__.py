"""Unit and functional test suite for SkyLines."""
import os
import shutil

from skylines.model import db

__all__ = ['setup_db', 'setup_app', 'teardown_db']


def setup_db():
    """Method used to build a database"""
    db.create_all()


def setup_dirs(app):
    filesdir = app.config['SKYLINES_FILES_PATH']
    if os.path.exists(filesdir):
        shutil.rmtree(filesdir)
    os.makedirs(filesdir)


def teardown_db():
    """Method used to destroy a database"""
    db.session.remove()
    db.drop_all()
    db.session.bind.dispose()


def clean_db():
    """Clean all data, leaving schema as is

    Suitable to be run before each db-aware test. This is much faster than
    dropping whole schema an recreating from scratch.
    """
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
