import os
import struct
from datetime import datetime
from hashlib import sha256

from sqlalchemy.types import (
    Unicode,
    Integer,
    BigInteger,
    SmallInteger,
    DateTime,
    Boolean,
    Interval,
    String,
)
from sqlalchemy.sql.expression import cast, case
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from skylines.database import db
from skylines.lib import files
from skylines.lib.sql import LowerCaseComparator
from skylines.lib.string import unicode_to_str, str_to_unicode
from skylines.lib.types import is_unicode, is_bytes

__all__ = ["User"]


class User(db.Model):
    """
    User definition.
    """

    __tablename__ = "users"
    __searchable_columns__ = ["name"]

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # Email address and name of the user

    email_address = db.column_property(
        db.Column(Unicode(255)), comparator_factory=LowerCaseComparator
    )

    first_name = db.Column(Unicode(255), nullable=False)
    last_name = db.Column(Unicode(255))

    # Hashed password

    _password = db.Column("password", Unicode(128), nullable=False)

    # The user's club (optional)

    club_id = db.Column(Integer, db.ForeignKey("clubs.id", ondelete="SET NULL"))
    club = db.relationship("Club", foreign_keys=[club_id], backref="members")

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
        return unicode_to_str(
            "<User: email=%s, display=%s>" % (self.email_address, self.name)
        )

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

    ##############################

    @hybrid_property
    def name(self):
        if not self.last_name:
            return self.first_name

        return self.first_name + u" " + self.last_name

    @name.expression
    def name_expression(cls):
        return case(
            [(cls.last_name != None, cls.first_name + u" " + cls.last_name)],
            else_=cls.first_name,
        )

    def initials(self):
        parts = self.name.split()
        initials = [p[0].upper() for p in parts if len(p) > 2 and "." not in p]
        return "".join(initials)

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
    def _hash_password(cls, password, salt=None):
        if salt is None:
            salt = os.urandom(60)

        assert is_unicode(password)
        assert is_bytes(salt)

        salt_hash = sha256()
        salt_hash.update(salt)

        hash = sha256()
        hash.update((password + salt_hash.hexdigest()).encode("utf-8"))

        return str_to_unicode(salt_hash.hexdigest() + hash.hexdigest())

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

        assert is_unicode(password)

        # Make sure accounts without a password can't log in
        if not self.password or not password:
            return False

        hash = sha256()
        hash.update((password + self.password[:64]).encode("utf-8"))

        return self.password[64:] == hash.hexdigest()

    ##############################

    def generate_tracking_key(self):
        self.tracking_key = struct.unpack("I", os.urandom(4))[0]

    @property
    def tracking_key_hex(self):
        if self.tracking_key is None:
            return None

        return "%X" % self.tracking_key

    @classmethod
    def tracking_delay_interval(cls):
        return cast(cast(cls.tracking_delay, String) + " minutes", Interval)

    ##############################

    @hybrid_method
    def is_manager(self):
        return self.admin

    ##############################

    def generate_recover_key(self, ip):
        self.recover_key = struct.unpack("I", os.urandom(4))[0] & 0x7FFFFFFF
        self.recover_time = datetime.utcnow()
        self.recover_ip = ip
        return self.recover_key

    ##############################

    def is_readable(self, user):
        """Does the current user have full read access to this object?"""
        return self.is_writable(user)

    def is_writable(self, user):
        return user and (
            self.id == user.id
            or (self.password is None and self.club_id == user.club_id)
            or user.is_manager()
        )

    ##############################

    def follows(self, other):
        assert isinstance(other, User)
        from skylines.model.follower import Follower

        return Follower.follows(self, other)

    @property
    def num_followers(self):
        from skylines.model.follower import Follower

        return Follower.query(destination=self).count()

    @property
    def num_following(self):
        from skylines.model.follower import Follower

        return Follower.query(source=self).count()

    ##############################

    def get_largest_flights(self):
        """
        Returns a query with all flights by the user
        as pilot ordered by distance
        """
        from skylines.model.flight import Flight

        return Flight.get_largest().filter(Flight.pilot == self)

    ##############################

    def delete(self):
        from skylines.model.igcfile import IGCFile

        for row in db.session.query(IGCFile).filter_by(owner_id=self.id):
            files.delete_file(row.filename)

        db.session.query(IGCFile).filter_by(owner_id=self.id).delete()
        db.session.delete(self)


db.Index(
    "users_lower_email_address_idx", db.func.lower(User.email_address), unique=True
)
