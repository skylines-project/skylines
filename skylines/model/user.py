import os
import struct
from datetime import datetime
from hashlib import sha256

from sqlalchemy.types import (
    Unicode, Integer, BigInteger, SmallInteger,
    DateTime, Boolean, Interval, String,
)
from sqlalchemy.sql.expression import cast, case
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from skylines.database import db
from skylines.lib.sql import LowerCaseComparator
from skylines.lib.formatter import units

__all__ = ['User']


class User(db.Model):
    """
    User definition.

    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.
    """

    __tablename__ = 'users'
    __searchable_columns__ = ['name']

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # Email address and name of the user

    email_address = db.column_property(
        db.Column(Unicode(255)), comparator_factory=LowerCaseComparator)

    first_name = db.Column(Unicode(255), nullable=False)
    last_name = db.Column(Unicode(255))

    # Hashed password

    _password = db.Column('password', Unicode(128), nullable=False)

    # The user's club (optional)

    club_id = db.Column(Integer, db.ForeignKey('clubs.id', ondelete='SET NULL'))
    club = db.relationship('Club', foreign_keys=[club_id], backref='members')

    # Tracking key, delay in minutes and other settings

    tracking_key = db.Column(BigInteger, nullable=False, index=True)
    tracking_delay = db.Column(SmallInteger, nullable=False, default=0)

    tracking_callsign = db.Column(Unicode(5))

    # Time and IP of creation

    created = db.Column(DateTime, default=datetime.utcnow)
    created_ip = db.Column(INET)

    # Time and IP of the last login

    login_time = db.Column(DateTime)
    login_ip = db.Column(INET)

    # Password recovery information

    recover_key = db.Column(Integer)
    recover_time = db.Column(DateTime)
    recover_ip = db.Column(INET)

    # Units settings

    distance_unit = db.Column(SmallInteger, nullable=False, default=1)
    speed_unit = db.Column(SmallInteger, nullable=False, default=1)
    lift_unit = db.Column(SmallInteger, nullable=False, default=0)
    altitude_unit = db.Column(SmallInteger, nullable=False, default=0)

    # Other settings

    admin = db.Column(Boolean, nullable=False, default=False)

    ##############################

    def __init__(self, *args, **kw):
        self.generate_tracking_key()
        super(User, self).__init__(*args, **kw)

    ##############################

    def __repr__(self):
        return ('<User: email=%s, display=%s>' % (
                self.email_address, self.name)).encode('unicode_escape')

    def __unicode__(self):
        return self.name

    ##############################

    @staticmethod
    def by_email_address(email):
        """Return the user object whose email address is ``email``."""
        return User.query(email_address=email).first()

    @staticmethod
    def by_credentials(email, password, *args, **kwargs):
        """
        Return the user object whose email address is ``email`` if the
        password is matching.
        """
        user = User.by_email_address(email)
        if user and user.validate_password(password):
            return user

    @staticmethod
    def by_tracking_key(key):
        return User.query(tracking_key=key).first()

    @staticmethod
    def by_recover_key(key):
        return User.query(recover_key=key).first()

    # Flask Login ################

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    ##############################

    @hybrid_property
    def name(self):
        if not self.last_name:
            return self.first_name

        return self.first_name + ' ' + self.last_name

    @name.expression
    def name_expression(cls):
        return case([
            (cls.last_name != None, cls.first_name + ' ' + cls.last_name),
        ], else_=cls.first_name)

    def initials(self):
        parts = self.name.split()
        initials = [p[0].upper() for p in parts if len(p) > 2 and '.' not in p]
        return ''.join(initials)

    ##############################

    @hybrid_property
    def password(self):
        """Return the hashed version of the password."""
        return self._password

    @password.setter
    def password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        self._password = self._hash_password(password)

    @classmethod
    def _hash_password(cls, password):
        # Make sure password is a str because we cannot hash unicode objects
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        salt = sha256()
        salt.update(os.urandom(60))
        hash = sha256()
        hash.update(password + salt.hexdigest())
        password = salt.hexdigest() + hash.hexdigest()
        # Make sure the hashed password is a unicode object at the end of the
        # process because SQLAlchemy _wants_ unicode objects for Unicode cols
        if not isinstance(password, unicode):
            password = password.decode('utf-8')
        return password

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool

        """

        # Make sure accounts without a password can't log in
        if not self.password or not password:
            return False

        hash = sha256()
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        hash.update(password + str(self.password[:64]))
        return self.password[64:] == hash.hexdigest()

    ##############################

    def generate_tracking_key(self):
        self.tracking_key = struct.unpack('I', os.urandom(4))[0]

    @property
    def tracking_key_hex(self):
        if self.tracking_key is None:
            return None

        return '%X' % self.tracking_key

    @classmethod
    def tracking_delay_interval(cls):
        return cast(cast(cls.tracking_delay, String) + ' minutes', Interval)

    ##############################

    @hybrid_method
    def is_manager(self):
        return self.admin

    ##############################

    def generate_recover_key(self, ip):
        self.recover_key = struct.unpack('I', os.urandom(4))[0] & 0x7fffffff
        self.recover_time = datetime.utcnow()
        self.recover_ip = ip
        return self.recover_key

    ##############################

    def is_readable(self, user):
        """Does the current user have full read access to this object?"""
        return self.is_writable(user)

    def is_writable(self, user):
        return user and \
            (self.id == user.id or
             (self.password is None and self.club_id == user.club_id) or
             user.is_manager())

    ##############################

    def follows(self, other):
        assert isinstance(other, User)
        from skylines.model.follower import Follower
        return Follower.follows(self, other)

    ##############################

    def get_largest_flights(self):
        """
        Returns a query with all flights by the user
        as pilot ordered by distance
        """
        from skylines.model.flight import Flight
        return Flight.get_largest().filter(Flight.pilot == self)

    ##############################

    @property
    def unit_preset(self):
        """Calculate unit preset based on user unit preference.

        If all user unit settings exactly matches one of the preset, return
        that preset id. Otherwise return 0, that is interpreted as 'Custom'
        preset.
        """
        for pref, preset in enumerate(units.UNIT_PRESETS):
            p = preset[1]
            if not p:
                continue
            eq = [p['distance_unit'] == units.DISTANCE_UNITS[self.distance_unit][0],
                  p['speed_unit'] == units.SPEED_UNITS[self.speed_unit][0],
                  p['lift_unit'] == units.LIFT_UNITS[self.lift_unit][0],
                  p['altitude_unit'] == units.ALTITUDE_UNITS[self.altitude_unit][0]
                  ]
            if all(eq):
                return pref

        return 0

    @unit_preset.setter
    def unit_preset(self, preset):
        """Set individual unit preferences according to given preset
        """
        name, settings = units.UNIT_PRESETS[preset]
        if settings:
            self.distance_unit = units.unitid(units.DISTANCE_UNITS,
                                              settings['distance_unit'])
            self.speed_unit = units.unitid(units.SPEED_UNITS,
                                           settings['speed_unit'])
            self.lift_unit = units.unitid(units.LIFT_UNITS,
                                          settings['lift_unit'])
            self.altitude_unit = units.unitid(units.ALTITUDE_UNITS,
                                              settings['altitude_unit'])


db.Index('users_lower_email_address_idx',
         db.func.lower(User.email_address), unique=True)
