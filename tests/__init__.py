"""Unit and functional test suite for SkyLines."""
import os
import shutil

from skylines.model import db
from tests.data.bootstrap import bootstrap


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
                cls.setup_db()

        if cls.SETUP_DIRS:
            cls.setup_dirs()

    # Tear down that database
    @classmethod
    def teardown_class(cls):
        if cls.SETUP_DB:
            with cls.app.app_context():
                cls.teardown_db()

    def setup(self):
        self.context = self.app.test_request_context()
        self.context.push()

        if self.BOOTSTRAP_DB:
            bootstrap()

    def teardown(self):
        if self.SETUP_DB:
            db.session.rollback()

        if self.BOOTSTRAP_DB:
            self.clean_db()
            db.session.commit()

        self.context.pop()

    @staticmethod
    def setup_db():
        """Method used to build a database"""
        db.create_all()

    @classmethod
    def setup_dirs(cls):
        filesdir = cls.app.config['SKYLINES_FILES_PATH']
        if os.path.exists(filesdir):
            shutil.rmtree(filesdir)
        os.makedirs(filesdir)

    @staticmethod
    def teardown_db():
        """Method used to destroy a database"""
        db.session.remove()
        db.drop_all()

    @staticmethod
    def clean_db():
        """Clean all data, leaving schema as is

        Suitable to be run before each db-aware test. This is much faster than
        dropping whole schema an recreating from scratch.
        """
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
