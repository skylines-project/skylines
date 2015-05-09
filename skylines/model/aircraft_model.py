from sqlalchemy.types import Integer, Unicode

from skylines.database import db


class AircraftModel(db.Model):
    __tablename__ = 'models'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    name = db.Column(Unicode(64), unique=True, nullable=False)

    # the kind of aircraft: 0=unspecified, 1=glider, 2=motor glider,
    # 3=paraglider, 4=hangglider, 5=ul glider
    kind = db.Column(Integer, nullable=False, default=0)

    igc_index = db.Column(Integer)

    # the index for the German DMSt
    dmst_index = db.Column(Integer)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return ('<AircraftModel: id=%d name=\'%s\' kind=\'%s\'>' % (self.id, self.name, self.kind)).encode('unicode_escape')

    def is_writable(self, user):
        return user and user.is_manager()

    @classmethod
    def by_name(cls, name):
        return cls.query(name=name).first()
