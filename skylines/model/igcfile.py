# -*- coding: utf-8 -*-

import re
from datetime import datetime

from sqlalchemy.sql.expression import and_
from sqlalchemy.types import Integer, DateTime, String, Unicode, Date

from skylines.database import db
from skylines.lib import files
from skylines.lib.igc import read_igc_headers


class IGCFile(db.Model):
    __tablename__ = 'igc_files'

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    owner_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', innerjoin=True)

    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    filename = db.Column(String(), nullable=False)
    md5 = db.Column(String(32), nullable=False, unique=True)

    logger_id = db.Column(String(3))
    logger_manufacturer_id = db.Column(String(3))

    registration = db.Column(Unicode(32))
    competition_id = db.Column(Unicode(5))
    model = db.Column(Unicode(64))

    date_utc = db.Column(Date, nullable=False)

    def __repr__(self):
        return ('<IGCFile: id=%d filename=\'%s\'>' % (self.id, self.filename)).encode('unicode_escape')

    @classmethod
    def by_md5(cls, _md5):
        return cls.query(md5=_md5).first()

    def is_writable(self, user):
        return user and \
            (self.owner_id == user.id or
             self.pilot_id == user.id or
             user.is_manager())

    def may_delete(self, user):
        return user and user.is_manager()

    def update_igc_headers(self):
        path = files.filename_to_path(self.filename)
        igc_headers = read_igc_headers(path)
        if igc_headers is None:
            return

        if 'manufacturer_id' in igc_headers:
            self.logger_manufacturer_id = igc_headers['manufacturer_id']

        if 'logger_id' in igc_headers:
            self.logger_id = igc_headers['logger_id']

        if 'date_utc' in igc_headers:
            self.date_utc = igc_headers['date_utc']

        if 'model' in igc_headers and (igc_headers['model'] is None or 0 < len(igc_headers['model']) < 64):
            self.model = igc_headers['model']

        if 'reg' in igc_headers and (igc_headers['reg'] is None or 0 < len(igc_headers['reg']) < 32):
            self.registration = igc_headers['reg']

        if 'cid' in igc_headers and (igc_headers['cid'] is None or 0 < len(igc_headers['cid']) < 5):
            self.competition_id = igc_headers['cid']

    def guess_registration(self):
        from skylines.model.flight import Flight

        # try to find another flight with the same logger and use it's aircraft registration
        if (self.logger_id is not None
                and self.logger_manufacturer_id is not None):
            logger_id = self.logger_id
            logger_manufacturer_id = self.logger_manufacturer_id

            result = Flight.query().join(IGCFile) \
                .filter(db.func.upper(IGCFile.logger_manufacturer_id) == db.func.upper(logger_manufacturer_id)) \
                .filter(db.func.upper(IGCFile.logger_id) == db.func.upper(logger_id)) \
                .filter(Flight.registration == None) \
                .order_by(Flight.id.desc())

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

            result = Flight.query() \
                .filter(db.func.upper(Flight.registration) == db.func.upper(glider_reg)) \
                .order_by(Flight.id.desc()) \
                .first()

            if result and result.model_id:
                return result.model_id

        # try to find another flight with the same logger and use it's aircraft type
        if (self.logger_id is not None
                and self.logger_manufacturer_id is not None):
            logger_id = self.logger_id
            logger_manufacturer_id = self.logger_manufacturer_id

            result = Flight.query().join(IGCFile) \
                .filter(db.func.upper(IGCFile.logger_manufacturer_id) == db.func.upper(logger_manufacturer_id)) \
                .filter(db.func.upper(IGCFile.logger_id) == db.func.upper(logger_id)) \
                .filter(Flight.model_id == None) \
                .order_by(Flight.id.desc())

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

            result = AircraftModel.query() \
                .filter(and_(
                    db.func.regexp_replace(db.func.lower(AircraftModel.name), '[^a-z]', ' ').like(db.func.any(text_fragments)),
                    db.func.regexp_replace(db.func.lower(AircraftModel.name), '[^0-9]', ' ').like(db.func.all(digit_fragments)))) \
                .order_by(db.func.levenshtein(db.func.regexp_replace(db.func.lower(AircraftModel.name), '[^a-z0-9]', ''), glider_type_clean))

            if result.first():
                return result.first().id

        # nothing found
        return None
