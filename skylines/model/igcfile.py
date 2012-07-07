# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, DateTime, String, Unicode
from skylines.model.auth import User
from skylines.model import DeclarativeBase, DBSession
from tg import config, request


class IGCFile(DeclarativeBase):
    __tablename__ = 'igc_files'

    id = Column(Integer, autoincrement=True, primary_key=True)
    owner_id = Column(Integer, ForeignKey('tg_user.user_id'), nullable=False)
    owner = relation('User', primaryjoin=(owner_id == User.user_id))
    time_created = Column(DateTime, nullable=False, default=datetime.now)
    filename = Column(String(), nullable=False)
    md5 = Column(String(32), nullable=False, unique=True)

    logger_id = Column(String(3))
    logger_manufacturer_id = Column(String(3))

    registration = Column(Unicode(32))
    model = Column(Unicode(64))

    @classmethod
    def by_md5(cls, _md5):
        return DBSession.query(cls).filter_by(md5=_md5).first()

    def get_download_uri(self):
        return config['skylines.files.uri'] + '/' + self.filename

    def is_writable(self):
        return request.identity and \
               (self.owner_id == request.identity['user'].user_id or
                self.pilot_id == request.identity['user'].user_id or
                'manage' in request.identity['permissions'])

    def may_delete(self):
        return request.identity and 'manage' in request.identity['permissions']

    def update_igc_headers(self):
        from skylines.lib.igc import read_igc_headers
        igc_headers = read_igc_headers(self.filename)

        if 'manufacturer_id' in igc_headers:
            self.logger_manufacturer_id = igc_headers['manufacturer_id']

        if 'logger_id' in igc_headers:
            self.logger_id = igc_headers['logger_id']

        if 'model' in igc_headers and 0 < len(igc_headers['model']) < 64:
            self.model = igc_headers['model']

        if 'reg' in igc_headers and 0 < len(igc_headers['reg']) < 32:
            self.registration = igc_headers['reg']
