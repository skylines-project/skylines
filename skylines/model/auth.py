# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.

It's perfectly fine to re-use this definition in the SkyLines application,
though.

"""
import os
import struct
from datetime import datetime
from hashlib import sha256

from sqlalchemy import Table, ForeignKey, Column, Index, func
from sqlalchemy.types import Unicode, Integer, BigInteger, SmallInteger, \
    DateTime, Boolean, Interval, String
from sqlalchemy.orm import relationship, synonym, column_property, backref
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects.postgresql import INET

from .base import DeclarativeBase, metadata
from skylines.lib.sql import LowerCaseComparator
from skylines.lib.formatter import units

__all__ = ['User', 'Group', 'Permission']

# Association tables


# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
group_permission_table = Table(
    'tg_group_permission', metadata,
    Column('group_id', Integer, ForeignKey('tg_group.id',
           onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Integer, ForeignKey('tg_permission.id',
           onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
user_group_table = Table(
    'tg_user_group', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.id',
           onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('tg_group.id',
           onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)


class User(DeclarativeBase):
    """
    User definition.

    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.
    """

    __tablename__ = 'tg_user'
    __searchable_columns__ = ['name']

    id = Column(Integer, autoincrement=True, primary_key=True)

    # eMail address and name of the user

    email_address = column_property(
        Column(Unicode(255)), comparator_factory=LowerCaseComparator)

    name = Column(Unicode(255), nullable=False)

    # Hashed password

    _password = Column('password', Unicode(128))

    # The user's club (optional)

    club_id = Column(Integer, ForeignKey('clubs.id', ondelete='SET NULL'))
    club = relationship('Club', foreign_keys=[club_id], backref='members')

    # Tracking key and delay in minutes

    tracking_key = Column(BigInteger, index=True)
    tracking_delay = Column(SmallInteger, nullable=False, default=0)

    # Time and IP of creation

    created = Column(DateTime, default=datetime.utcnow)
    created_ip = Column(INET)

    # Time and IP of the last login

    login_time = Column(DateTime)
    login_ip = Column(INET)

    # Password recovery information

    recover_key = Column(Integer)
    recover_time = Column(DateTime)
    recover_ip = Column(INET)

    # Units settings

    distance_unit = Column(SmallInteger, nullable=False, default=1)
    speed_unit = Column(SmallInteger, nullable=False, default=1)
    lift_unit = Column(SmallInteger, nullable=False, default=0)
    altitude_unit = Column(SmallInteger, nullable=False, default=0)

    # Other settings

    eye_candy = Column(Boolean, nullable=False, default=False)

    ##############################

    def __repr__(self):
        return ('<User: email=%s, display=%s>' % (
                self.email_address, self.name)).encode('utf-8')

    def __unicode__(self):
        return self.name

    ##############################

    @classmethod
    def by_email_address(cls, email):
        """Return the user object whose email address is ``email``."""
        return cls.query(email_address=email).first()

    @classmethod
    def by_credentials(cls, email, password):
        """
        Return the user object whose email address is ``email`` if the
        password is matching.
        """
        user = cls.query(email_address=email).first()
        if user and user.validate_password(password):
            return user

    @classmethod
    def by_tracking_key(cls, key):
        return cls.query(tracking_key=key).first()

    @classmethod
    def by_recover_key(cls, key):
        return cls.query(recover_key=key).first()

    ## Flask Login ###############

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    ##############################

    def initials(self):
        parts = self.name.split()
        initials = [p[0].upper() for p in parts if len(p) > 2 and '.' not in p]
        return ''.join(initials)

    ##############################

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        self._password = self._hash_password(password)

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym(
        '_password', descriptor=property(_get_password, _set_password))

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
        if not self.password:
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

    @property
    def permissions(self):
        """Return a set with all permissions granted to the user."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    ##############################

    def generate_recover_key(self, ip):
        self.recover_key = struct.unpack('I', os.urandom(4))[0] & 0x7fffffff
        self.recover_time = datetime.utcnow()
        self.recover_ip = ip
        return self.recover_key

    ##############################

    def is_readable(self, identity):
        """Does the current user have full read access to this object?"""
        return self.is_writable(identity)

    def is_writable(self, identity):
        return identity and \
            (self.id == identity['user'].id or
             (self.password is None and self.club_id == identity['user'].club_id) or
             'manage' in identity['permissions'])

    ##############################

    def follows(self, other):
        assert isinstance(other, User)
        from skylines.model.follower import Follower
        return Follower.follows(self, other)

    ##############################

    def get_largest_flights(self):
        '''
        Returns a query with all flights by the user
        as pilot ordered by distance
        '''
        from skylines.model.flight import Flight
        return Flight.get_largest().filter_by(pilot=self)

    ##############################

    @property
    def unit_preset(self):
        """Calculate unit preset based on user unit preference.

        If all user unit settings exactly matches one of the preset, return
        that preset id. Otherwise return 0, that is interpreted as 'Custom'
        preset.
        """
        for pref, preset in enumerate(units.unit_presets):
            p = preset[1]
            if not p:
                continue
            eq = [p['distance_unit'] == units.distance_units[self.distance_unit][0],
                  p['speed_unit'] == units.speed_units[self.speed_unit][0],
                  p['lift_unit'] == units.lift_units[self.lift_unit][0],
                  p['altitude_unit'] == units.altitude_units[self.altitude_unit][0]
                  ]
            if all(eq):
                return pref

        return 0

    @unit_preset.setter
    def unit_preset(self, preset):
        """Set individual unit preferences according to given preset
        """
        name, settings = units.unit_presets[preset]
        if settings:
            self.distance_unit = units.unitid(units.distance_units,
                                              settings['distance_unit'])
            self.speed_unit = units.unitid(units.speed_units,
                                           settings['speed_unit'])
            self.lift_unit = units.unitid(units.lift_units,
                                          settings['lift_unit'])
            self.altitude_unit = units.unitid(units.altitude_units,
                                              settings['altitude_unit'])


Index('users_lower_email_address_idx',
      func.lower(User.email_address), unique=True)


class Group(DeclarativeBase):
    """
    Group definition for :mod:`repoze.what`.

    Only the ``group_name`` column is required by :mod:`repoze.what`.

    """

    __tablename__ = 'tg_group'

    # Columns

    id = Column(Integer, autoincrement=True, primary_key=True)

    group_name = Column(Unicode(16), unique=True, nullable=False)

    name = Column(Unicode(255))

    created = Column(DateTime, default=datetime.utcnow)

    # Relations

    users = relationship('User', secondary=user_group_table, backref='groups')

    # Special methods

    def __repr__(self):
        return ('<Group: name=%s>' % self.group_name).encode('utf-8')

    def __unicode__(self):
        return self.group_name


class Permission(DeclarativeBase):
    """
    Permission definition for :mod:`repoze.what`.

    Only the ``permission_name`` column is required by :mod:`repoze.what`.

    """

    __tablename__ = 'tg_permission'

    # Columns

    id = Column(Integer, autoincrement=True, primary_key=True)

    permission_name = Column(Unicode(63), unique=True, nullable=False)

    description = Column(Unicode(255))

    # Relations

    groups = relationship(
        'Group', secondary=group_permission_table,
        backref=backref('permissions', lazy='joined'))

    # Special methods

    def __repr__(self):
        return ('<Permission: name=%s>' % self.permission_name).encode('utf-8')

    def __unicode__(self):
        return self.permission_name
