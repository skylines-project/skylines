from datetime import datetime

from sqlalchemy import Table, Column, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Unicode, UnicodeText, DateTime, Date

from .base import DeclarativeBase, metadata


# This is the association table for the many-to-many relationship between
# competitions and their admins.
competition_admin_table = Table(
    'competition_admins', metadata,
    Column('competition_id', Integer, ForeignKey('competitions.id',
           onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('user_id', Integer, ForeignKey('tg_user.id',
           onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)


class Competition(DeclarativeBase):
    """
    This table describes an airsport competition.

    Each competition needs to have a name and start and end dates.
    It also has a list of participants (organizers and pilots) and can
    optionally have information on where it is taking place.
    """

    __tablename__ = 'competitions'
    __searchable_columns__ = ['name']
    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='date_check'),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)

    # Name of the competition

    name = Column(Unicode(64), nullable=False)

    # Description text for the competition (optional)

    description = Column(UnicodeText)

    # Competition time
    #
    # start_date has to be smaller or equal to end_date

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Competition organizers and pilots

    admins = relationship('User', secondary=competition_admin_table)

    participants = relationship('CompetitionParticipation')

    # Metadata

    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = Column(DateTime, nullable=False, default=datetime.utcnow)

    creator_id = Column(Integer, ForeignKey('tg_user.id', ondelete='SET NULL'))
    creator = relationship('User')

    # Location of the competition (optional)

    location = Column(Unicode(64))

    # Competition airport (optional)

    airport_id = Column(Integer, ForeignKey('airports.id', ondelete='SET NULL'))
    airport = relationship('Airport')

    # Competitions classes

    classes = relationship('CompetitionClass')

    ##############################

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Competition: id={} name=\'{}\'>' \
            .format(self.id, self.name).encode('utf-8')

    ##############################

    @property
    def location_string(self):
        """ A string containing the location of the competition. """

        if self.location and len(self.location) != 0:
            return self.location

        if self.airport_id:
            return self.airport.name


class CompetitionParticipation(DeclarativeBase):
    """
    This table describes the many-to-many relationship between
    competitions and pilots and their type of relationship.

    Admins can change the details of the competition and add new pilots
    and other admins to the competition.
    """

    __tablename__ = 'competition_participation'
    __table_args__ = (
        UniqueConstraint(
            'competition_id', 'user_id', name='unique_participation'),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)

    # The competition that this class definition belongs to

    competition_id = Column(
        Integer, ForeignKey('competitions.id', ondelete='CASCADE'),
        nullable=False)
    competition = relationship('Competition', innerjoin=True)

    # SkyLines user account

    user_id = Column(
        Integer, ForeignKey('tg_user.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', innerjoin=True)

    # Competition class (optional)

    class_id = Column(
        Integer, ForeignKey('competition_classes.id', ondelete='SET NULL'))
    class_ = relationship('CompetitionClass')

    # Timestamps

    join_time = Column(DateTime)

    ##############################

    def __repr__(self):
        return '<CompetitionParticipation: id={}>' \
            .format(self.id).encode('utf-8')


class CompetitionClass(DeclarativeBase):
    """
    This table describes a competition class.

    The use of competition classes should be optional, for competitions
    that don't have classes.
    """

    __tablename__ = 'competition_classes'

    id = Column(Integer, autoincrement=True, primary_key=True)

    # The competition that this class definition belongs to

    competition_id = Column(
        Integer, ForeignKey('competitions.id', ondelete='CASCADE'),
        nullable=False)
    competition = relationship('Competition', innerjoin=True)

    # Name of the competition class

    name = Column(Unicode(64), nullable=False)

    # Description of the competition class (optional)

    description = Column(UnicodeText)

    # Competition class pilots

    participants = relationship('CompetitionParticipation')

    ##############################

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<CompetitionClass: id={} name=\'{}\'>' \
            .format(self.id, self.name).encode('utf-8')
