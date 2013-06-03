from .search import search_query
from skylines import db


def monkey_patch_model():
    def query(cls, **kw):
        q = db.session.query(cls)

        if kw:
            q = q.filter_by(**kw)

        return q

    def get(cls, id):
        return cls.query().get(id)

    db.Model.flask_query = db.Model.query
    db.Model.query = classmethod(query)
    db.Model.get = classmethod(get)
    db.Model.search_query = classmethod(search_query)


monkey_patch_model()

metadata = db.metadata
