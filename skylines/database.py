from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate


def query(cls, **kw):
    q = db.session.query(cls)

    if kw:
        q = q.filter_by(**kw)

    return q


def get(cls, id):
    return cls.query().get(id)


def exists(cls, **kw):
    return cls.query(**kw).first() is not None


db = SQLAlchemy(session_options=dict(expire_on_commit=False))
migrate = Migrate()

db.Model.flask_query = db.Model.query
db.Model.query = classmethod(query)
db.Model.get = classmethod(get)
db.Model.exists = classmethod(exists)
