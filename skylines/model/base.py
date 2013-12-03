from .search import search_query
from skylines.model import db


def monkey_patch_model():
    def query(cls, **kw):
        q = db.session.query(cls)

        if kw:
            q = q.filter_by(**kw)

        return q

    def get(cls, id):
        return cls.query().get(id)

    def exists(cls, **kw):
        return cls.query(**kw).first() is not None

    db.Model.flask_query = db.Model.query
    db.Model.query = classmethod(query)
    db.Model.get = classmethod(get)
    db.Model.exists = classmethod(exists)
    db.Model.search_query = classmethod(search_query)


monkey_patch_model()
