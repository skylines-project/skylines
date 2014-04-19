# -*- coding: utf-8 -*-

# flake8: noqa

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options=dict(expire_on_commit=False))

import skylines.model.base

# Import your model modules here.
from .aircraft_model import AircraftModel
from .airport import Airport
from .airspace import Airspace
from .club import Club
from .elevation import Elevation
from .event import Event, Notification
from .flight import Flight, FlightPathChunks
from .flight_meetings import FlightMeetings
from .flight_comment import FlightComment
from .flight_phase import FlightPhase
from .follower import Follower
from .geo import Location, Bounds
from .igcfile import IGCFile
from .mountain_wave_project import MountainWaveProject
from .timezone import TimeZone
from .trace import Trace
from .tracking import TrackingFix, TrackingSession
from .user import User
