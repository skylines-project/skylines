"""Unit and functional test suite for SkyLines."""
import os
import shutil

from skylines.model import db
from tests.data.bootstrap import bootstrap

__all__ = ['setup_db', 'setup_app', 'teardown_db']


def setup_db():
    """Method used to build a database"""
    db.create_all()


def setup_dirs(app):
    filesdir = app.config['SKYLINES_FILES_PATH']
    if os.path.exists(filesdir):
        shutil.rmtree(filesdir)
    os.makedirs(filesdir)


def setup_app(app):
    setup_db()
    setup_dirs(app)


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


def clean_db_and_bootstrap():
    clean_db()
    bootstrap()
    db.session.commit()


class AppTest(object):

    SETUP_DB = True
    BOOTSTRAP_DB = False

    SETUP_DIRS = False

    def create_app(self):
        import config
        from skylines.app import create_app
        return create_app(config_file=config.TESTING_CONF_PATH)

    @classmethod
    def setup_class(cls):
        cls.app = cls().create_app()

        if cls.SETUP_DB:
            with cls.app.app_context():
                setup_db()

        if cls.SETUP_DIRS:
            setup_dirs(cls.app)

    # Tear down that database
    @classmethod
    def teardown_class(cls):
        if cls.SETUP_DB:
            with cls.app.app_context():
                teardown_db()

    def setup(self):
        self.context = self.app.test_request_context()
        self.context.push()

        if self.BOOTSTRAP_DB:
            bootstrap()

    def teardown(self):
        if self.SETUP_DB:
            db.session.rollback()

        if self.BOOTSTRAP_DB:
            clean_db()
            db.session.commit()

        self.context.pop()
