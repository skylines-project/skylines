# -*- coding: utf-8 -*-

from datetime import datetime
import re
from sqlalchemy import ForeignKey, Column, func
from sqlalchemy.orm import relation
from sqlalchemy.sql.expression import desc, and_
from sqlalchemy.types import Integer, DateTime, String, Unicode, Date
from skylines.lib.igc import read_igc_headers
from skylines.model.base import DeclarativeBase
from skylines.model.session import DBSession
from skylines.model.auth import User
from tg import config


class IGCFile(DeclarativeBase):
    __tablename__ = 'igc_files'

    id = Column(Integer, autoincrement=True, primary_key=True)
    owner_id = Column(Integer, ForeignKey('tg_user.id'), nullable=False)
    owner = relation('User', primaryjoin=(owner_id == User.id))
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    filename = Column(String(), nullable=False)
    md5 = Column(String(32), nullable=False, unique=True)

    logger_id = Column(String(3))
    logger_manufacturer_id = Column(String(3))

    registration = Column(Unicode(32))
    competition_id = Column(Unicode(5))
    model = Column(Unicode(64))

    date_utc = Column(Date, nullable=False)

    def __repr__(self):
        return ('<IGCFile: id=%d filename=\'%s\'>' % (self.id, self.filename)).encode('utf-8')

    @classmethod
    def by_md5(cls, _md5):
        return DBSession.query(cls).filter_by(md5=_md5).first()

    def get_download_uri(self):
        return config['skylines.files.uri'] + '/' + self.filename

    def is_writable(self, identity):
        return identity and \
               (self.owner_id == identity['user'].id or
                self.pilot_id == identity['user'].id or
                'manage' in identity['permissions'])

    def may_delete(self, identity):
        return identity and 'manage' in identity['permissions']

    def update_igc_headers(self):
        igc_headers = read_igc_headers(self.filename)
        if igc_headers is None:
            return

        if 'manufacturer_id' in igc_headers:
            self.logger_manufacturer_id = igc_headers['manufacturer_id']

        if 'logger_id' in igc_headers:
            self.logger_id = igc_headers['logger_id']

        if 'date_utc' in igc_headers:
            self.date_utc = igc_headers['date_utc']

        if 'model' in igc_headers and 0 < len(igc_headers['model']) < 64:
            self.model = igc_headers['model']

        if 'reg' in igc_headers and 0 < len(igc_headers['reg']) < 32:
            self.registration = igc_headers['reg']

        if 'cid' in igc_headers and 0 < len(igc_headers['cid']) < 5:
            self.competition_id = igc_headers['cid']

    def guess_registration(self):
        from skylines.model.flight import Flight

        # try to find another flight with the same logger and use it's aircraft registration
        if self.logger_id is not None \
            and self.logger_manufacturer_id is not None:
            logger_id = self.logger_id
            logger_manufacturer_id = self.logger_manufacturer_id

            result = DBSession.query(Flight).outerjoin(IGCFile) \
                .filter(func.upper(IGCFile.logger_manufacturer_id) == func.upper(logger_manufacturer_id)) \
                .filter(func.upper(IGCFile.logger_id) == func.upper(logger_id)) \
                .filter(Flight.registration != None) \
                .order_by(desc(Flight.id))

            if self.logger_manufacturer_id.startswith('X'):
                result = result.filter(Flight.pilot == self.owner)

            result = result.first()

            if result and result.registration:
                return result.registration

        return None

    def guess_model(self):
        from skylines.model import Flight, AircraftModel

        # first try to find the reg number in the database
        if self.registration is not None:
            glider_reg = self.registration

            result = DBSession.query(Flight) \
                .filter(func.upper(Flight.registration) == func.upper(glider_reg)) \
                .order_by(desc(Flight.id)) \
                .first()

            if result and result.model_id:
                return result.model_id

        # try to find another flight with the same logger and use it's aircraft type
        if self.logger_id is not None \
            and self.logger_manufacturer_id is not None:
            logger_id = self.logger_id
            logger_manufacturer_id = self.logger_manufacturer_id

            result = DBSession.query(Flight).outerjoin(IGCFile) \
                .filter(func.upper(IGCFile.logger_manufacturer_id) == func.upper(logger_manufacturer_id)) \
                .filter(func.upper(IGCFile.logger_id) == func.upper(logger_id)) \
                .filter(Flight.model_id != None) \
                .order_by(desc(Flight.id))

            if self.logger_manufacturer_id.startswith('X'):
                result = result.filter(Flight.pilot == self.owner)

            result = result.first()

            if result and result.model_id:
                return result.model_id

        if self.model is not None:
            glider_type = self.model.lower()

            # otherwise, try to guess the glider model by the glider type igc header
            text_fragments = ['%{}%'.format(v) for v in re.sub(r'[^a-z]', ' ', glider_type).split()]
            digit_fragments = ['%{}%'.format(v) for v in re.sub(r'[^0-9]', ' ', glider_type).split()]

            if not text_fragments and not digit_fragments:
                return None

            glider_type_clean = re.sub(r'[^a-z0-9]', '', glider_type)

            result = DBSession.query(AircraftModel) \
                .filter(and_( \
                    func.regexp_replace(func.lower(AircraftModel.name), '[^a-z]', ' ').like(func.any(text_fragments)), \
                    func.regexp_replace(func.lower(AircraftModel.name), '[^0-9]', ' ').like(func.all(digit_fragments)))) \
                .order_by(func.levenshtein(func.regexp_replace(func.lower(AircraftModel.name), '[^a-z0-9]', ''), glider_type_clean))

            if result.first():
                return result.first().id

        # nothing found
        return None
