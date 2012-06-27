# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Float, DateTime
from skylines.model.auth import User
from skylines.model import DeclarativeBase


class TrackingFix(DeclarativeBase):
    __tablename__ = 'tracking_fixes'

    id = Column(Integer, autoincrement=True, primary_key=True)

    time = Column(DateTime, nullable=False, default=datetime.now)

    latitude = Column(Float)
    longitude = Column(Float)
    track = Column(Integer)
    ground_speed = Column(Float)
    airspeed = Column(Float)
    altitude = Column(Integer)
    vario = Column(Float)
    engine_noise_level = Column(Integer)

    pilot_id = Column(Integer,
                      ForeignKey('tg_user.user_id', use_alter=True,
                                 name="tg_user.user_id"), nullable=False)

    pilot = relation('User', primaryjoin=(pilot_id == User.user_id))
