import sys
import nose
from nose.tools import eq_, assert_raises

from skylines import db
from skylines.tests import setup_db, teardown_db
from sqlalchemy import Column, Integer, String, Unicode


def setup():
    # Setup the database
    setup_db()
    db.session.add(TestTable(name='John Doe', uni='Jane and John Doe'))
    db.session.commit()


def teardown():
    # Remove the database again
    teardown_db()


class TestTable(db.Model):
    __tablename__ = 'ilike_test'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32))
    uni = Column(Unicode(32))


def test_weighted_ilike():
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


def test_weighted_ilike_exception():
    """ String.weighted_ilike() fails as expected """

    assert_raises(AssertionError, TestTable.name.weighted_ilike, '%John%', '5')


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
