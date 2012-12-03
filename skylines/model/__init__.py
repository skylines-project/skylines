# -*- coding: utf-8 -*-
"""The application's model objects"""

from skylines.model.base import metadata
from skylines.model.session import DBSession, init_model

# Import your model modules here.
from skylines.model.auth import User, Group, Permission
from skylines.model.aircraft_model import AircraftModel
from skylines.model.flight import Flight
from skylines.model.flight_comment import FlightComment
from skylines.model.flight_phase import FlightPhase
from skylines.model.igcfile import IGCFile
from skylines.model.club import Club
from skylines.model.tracking import TrackingFix
from skylines.model.geo import Location
from skylines.model.airport import Airport
from skylines.model.follower import Follower
from skylines.model.airspace import Airspace
from skylines.model.timezone import TimeZone
from skylines.model.trace import Trace
from skylines.model.notification import Notification
