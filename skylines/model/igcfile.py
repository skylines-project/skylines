# -*- coding: utf-8 -*-

import re, StringIO
from datetime import datetime

from sqlalchemy.sql.expression import and_
from sqlalchemy.types import Integer, DateTime, String, Unicode, Date

from skylines.database import db
from skylines.lib import files
from skylines.lib.igc import read_igc_headers, read_condor_fpl
from skylines.lib.string import unicode_to_str
from skylines.lib.md5 import file_md5
from skylines.lib.files import read_file, write_file

class IGCFile(db.Model):
    __tablename__ = "igc_files"

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    owner_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", innerjoin=True)

    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    filename = db.Column(String(), nullable=False)
    is_condor_file = db.Column(db.Boolean, default = False)
    landscape = db.Column(String(32), nullable=False)
    flight_plan_md5 = db.Column(String(32), nullable=False)
    md5 = db.Column(String(32), nullable=False, unique=True)

    logger_id = db.Column(String(3))
    logger_manufacturer_id = db.Column(String(3))

    registration = db.Column(Unicode(32))
    competition_id = db.Column(Unicode(5))
    model = db.Column(Unicode(64))

    date_utc = db.Column(Date, nullable=False)
    date_condor = db.Column(Date, nullable=False)

    def __repr__(self):
        return unicode_to_str(
            "<IGCFile: id=%d filename='%s'>" % (self.id, self.filename)
        )

    @classmethod
    def by_md5(cls, _md5):
        return cls.query(md5=_md5).first()

    def is_writable(self, user):
        return user and (
            self.owner_id == user.id or self.pilot_id == user.id or user.is_manager()
        )

    def may_delete(self, user):
        return user and user.is_manager()

    def update_igc_headers(self):
        path = files.filename_to_path(self.filename)
        igc_headers = read_igc_headers(path)
        condor_fpl,landscape = read_condor_fpl(path)
        if igc_headers is None:
            return

        if len(condor_fpl) > 0:
            self.is_condor_file = True
            self.landscape = landscape
            self.flight_plan_md5 = file_md5(StringIO.StringIO('\n'.join(condor_fpl)))

        if "manufacturer_id" in igc_headers:
            self.logger_manufacturer_id = igc_headers["manufacturer_id"]

        if "logger_id" in igc_headers:
            self.logger_id = igc_headers["logger_id"]

        if "date_utc" in igc_headers:
            self.date_utc = igc_headers["date_utc"]

        if "model" in igc_headers and (
            igc_headers["model"] is None or 0 < len(igc_headers["model"]) < 64
        ):
            self.model = igc_headers["model"]

        if "reg" in igc_headers and (
            igc_headers["reg"] is None or 0 < len(igc_headers["reg"]) < 32
        ):
            self.registration = igc_headers["reg"]

        if "cid" in igc_headers and (
            igc_headers["cid"] is None or 0 < len(igc_headers["cid"]) < 5
        ):
            self.competition_id = igc_headers["cid"]

    def get_model(self):
        from skylines.model import AircraftModel

        if self.model is not None:
            result = (
                AircraftModel.query()
                .filter(AircraftModel.name == self.model)
            )
            if result.first():
                return result.first().id
        # nothing found
        return None
