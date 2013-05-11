import sys
import nose
from nose.tools import eq_, assert_raises

import transaction
from skylines.model.base import DeclarativeBase
from skylines.model import DBSession
from skylines.tests import setup_app, teardown_db
from sqlalchemy import Column, Integer, String, Unicode


def setup():
    # Setup the database
    DBSession.remove()
    transaction.begin()
    setup_app()

    DBSession.add(TestTable(name='John Doe', uni='Jane and John Doe'))


def teardown():
    # Remove the database again
    DBSession.rollback()
    teardown_db()


class TestTable(DeclarativeBase):
    __tablename__ = 'ilike_test'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32))
    uni = Column(Unicode(32))


def test_weighted_ilike():
    """ String.weighted_ilike() works as expected """

    eq_(DBSession.query(
        TestTable.name.weighted_ilike('%John%', 1)).scalar(), 1)
    eq_(DBSession.query(
        TestTable.name.weighted_ilike('%John%', 5)).scalar(), 5)
    eq_(DBSession.query(
        TestTable.name.weighted_ilike('%John%', 100)).scalar(), 100)

    eq_(DBSession.query(
        TestTable.name.weighted_ilike('%John%')).scalar(), 1)

    eq_(float(DBSession.query(
        TestTable.name.weighted_ilike('%John%', 0.1)).scalar()), 0.1)


def test_weighted_ilike_exception():
    """ String.weighted_ilike() fails as expected """

    assert_raises(AssertionError, TestTable.name.weighted_ilike, '%John%', '5')


if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
