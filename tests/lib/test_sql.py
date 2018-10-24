import pytest

from sqlalchemy import Column, Integer, String, Unicode

from skylines.database import db
from skylines.lib import sql
from skylines.lib.types import is_unicode


class ExampleTable(db.Model):
    __tablename__ = "ilike_test"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32))
    uni = Column(Unicode(32))


@pytest.mark.usefixtures("db_session")
class TestSqlLib:
    def setup(self):
        db.session.add(ExampleTable(name="John Doe", uni=u"Jane and John Doe"))
        db.session.commit()

    def test_weighted_ilike(self):
        """ String.weighted_ilike() works as expected """

        assert (
            db.session.query(ExampleTable.name.weighted_ilike("%John%", 1)).scalar()
            == 1
        )
        assert (
            db.session.query(ExampleTable.name.weighted_ilike("%John%", 5)).scalar()
            == 5
        )
        assert (
            db.session.query(ExampleTable.name.weighted_ilike("%John%", 100)).scalar()
            == 100
        )

        assert (
            db.session.query(ExampleTable.name.weighted_ilike("%John%")).scalar() == 1
        )

        assert (
            float(
                db.session.query(
                    ExampleTable.name.weighted_ilike("%John%", 0.1)
                ).scalar()
            )
            == 0.1
        )

    def test_weighted_ilike_exception(self):
        """ String.weighted_ilike() fails as expected """

        with pytest.raises(AssertionError):
            ExampleTable.name.weighted_ilike("%John%", "5")


def test_query_to_sql(db_session):
    input = ExampleTable(name="John Doe", uni=u"Jane and John Doe")
    db_session.add(input)
    db_session.commit()

    query = (
        db_session.query(ExampleTable)
        .filter_by(id=input.id)
        .order_by(ExampleTable.name)
    )

    sql_text = sql.query_to_sql(query)

    assert is_unicode(sql_text)
    assert (
        sql_text
        == "SELECT ilike_test.id, ilike_test.name, ilike_test.uni \n"
        + "FROM ilike_test \n"
        + "WHERE ilike_test.id = {} ORDER BY ilike_test.name".format(input.id)
    )


def test_query_to_sql2(db_session):
    from geoalchemy2.shape import from_shape
    from sqlalchemy.sql import literal_column
    from shapely.geometry import LineString

    linestring = LineString([(0, 0), (1, 2), (3, 4)])
    locations = from_shape(linestring, srid=4326)

    one = literal_column("1 as flight_id")
    query = db_session.query(locations.label("flight_geometry"), one)

    sql_text = sql.query_to_sql(query)

    assert is_unicode(sql_text)
    assert (
        sql_text
        == u"SELECT ST_GeomFromWKB('\\001\\002\\000\\000\\000\\003\\000\\000\\000\\000\\000\\000\\000"
        + "\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\000\\360?\\000"
        + "\\000\\000\\000\\000\\000\\000@\\000\\000\\000\\000\\000\\000\\010@\\000\\000\\000\\000\\000\\000"
        + "\\020@'::bytea, 4326) AS flight_geometry, 1 as flight_id"
    )
