import sys
import nose
from nose.tools import eq_, assert_raises

from tests import setup_db, teardown_db
from sqlalchemy import Column, Integer, String, Unicode

from skylines import create_app
from skylines.model import db


class TestTable(db.Model):
    __tablename__ = 'ilike_test'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32))
    uni = Column(Unicode(32))


class TestSqlLib:

    @classmethod
    def setup_class(cls):
        cls.app = create_app()

    def setup(self):
        self.context = self.app.app_context()
        self.context.push()

        # Setup the database
        setup_db()
        db.session.add(TestTable(name='John Doe', uni='Jane and John Doe'))
        db.session.commit()

    def teardown(self):
        # Remove the database again
        teardown_db()

        self.context.pop()

    def test_weighted_ilike(self):
        """ String.weighted_ilike() works as expected """

        eq_(db.session.query(
            TestTable.name.weighted_ilike('%John%', 1)).scalar(), 1)
        eq_(db.session.query(
            TestTable.name.weighted_ilike('%John%', 5)).scalar(), 5)
        eq_(db.session.query(
            TestTable.name.weighted_ilike('%John%', 100)).scalar(), 100)

        eq_(db.session.query(
            TestTable.name.weighted_ilike('%John%')).scalar(), 1)

        eq_(float(db.session.query(
            TestTable.name.weighted_ilike('%John%', 0.1)).scalar()), 0.1)

    def test_weighted_ilike_exception(self):
        """ String.weighted_ilike() fails as expected """

        assert_raises(AssertionError, TestTable.name.weighted_ilike, '%John%', '5')


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
