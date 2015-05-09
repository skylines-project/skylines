import pytest

from sqlalchemy import Column, Integer, String, Unicode

from skylines.database import db


class ExampleTable(db.Model):
    __tablename__ = 'ilike_test'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32))
    uni = Column(Unicode(32))


@pytest.mark.usefixtures("db_session")
class TestSqlLib:

    def setup(self):
        db.session.add(ExampleTable(name='John Doe', uni='Jane and John Doe'))
        db.session.commit()

    def test_weighted_ilike(self):
        """ String.weighted_ilike() works as expected """

        assert db.session.query(
            ExampleTable.name.weighted_ilike('%John%', 1)).scalar() == 1
        assert db.session.query(
            ExampleTable.name.weighted_ilike('%John%', 5)).scalar() == 5
        assert db.session.query(
            ExampleTable.name.weighted_ilike('%John%', 100)).scalar() == 100

        assert db.session.query(
            ExampleTable.name.weighted_ilike('%John%')).scalar() == 1

        assert float(db.session.query(
            ExampleTable.name.weighted_ilike('%John%', 0.1)).scalar()) == 0.1

    def test_weighted_ilike_exception(self):
        """ String.weighted_ilike() fails as expected """

        with pytest.raises(AssertionError):
            ExampleTable.name.weighted_ilike('%John%', '5')
