# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode

from skylines import db


class AircraftModel(db.Model):
    __tablename__ = 'models'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64), unique=True, nullable=False)

    # the kind of aircraft: 0=unspecified, 1=glider, 2=motor glider,
    # 3=paraglider, 4=hangglider, 5=ul glider
    kind = Column(Integer, nullable=False, default=0)

    igc_index = Column(Integer)

    # the index for the German DMSt
    dmst_index = Column(Integer)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return ('<AircraftModel: id=%d name=\'%s\'>' % (self.id, self.name)).encode('utf-8')

    def is_writable(self, identity):
        return identity and 'manage' in identity['permissions']

    @classmethod
    def by_name(cls, name):
        return cls.query(name=name).first()
