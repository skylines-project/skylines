from .search import search_query
from skylines import db


def query(cls, **kw):
    q = db.session.query(cls)

    if kw:
        q = q.filter_by(**kw)

    return q


def get(cls, id):
    return cls.query().get(id)


DeclarativeBase = db.Model
DeclarativeBase.flask_query = DeclarativeBase.query
DeclarativeBase.query = classmethod(query)
DeclarativeBase.get = classmethod(get)
DeclarativeBase.search_query = classmethod(search_query)

metadata = db.metadata
