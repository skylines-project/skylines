# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from .session import DBSession


class _BaseClass(object):
    @classmethod
    def query(cls, **kw):
        q = DBSession.query(cls)

        if kw:
            q = q.filter_by(**kw)

        return q

    @classmethod
    def get(cls, id):
        return cls.query().get(id)


# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
DeclarativeBase = declarative_base(cls=_BaseClass)

# There are two convenient ways for you to spare some typing.
# You can have a query property on all your model classes by doing this:
# DeclarativeBase.query = DBSession.query_property()
# Or you can use a session-aware mapper as it was used in TurboGears 1:
# DeclarativeBase = declarative_base(mapper=DBSession.mapper)

# Global metadata.
# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata
