from datetime import datetime

from sqlalchemy.types import Integer, Unicode, UnicodeText, DateTime, Date

from skylines import db


# This is the association table for the many-to-many relationship between
# competitions and their admins.
competition_admin_table = db.Table(
    'competition_admins', db.metadata,
    db.Column('competition_id', Integer, db.ForeignKey('competitions.id',
              onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    db.Column('user_id', Integer, db.ForeignKey('tg_user.id',
              onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)


class Competition(db.Model):
    """
    This table describes an airsport competition.

    Each competition needs to have a name and start and end dates.
    It also has a list of participants (organizers and pilots) and can
    optionally have information on where it is taking place.
    """

    __tablename__ = 'competitions'
    __searchable_columns__ = ['name']
    __table_args__ = (
        db.CheckConstraint('end_date >= start_date', name='date_check'),
    )

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # Name of the competition

    name = db.Column(Unicode(64), nullable=False)

    # Description text for the competition (optional)

    description = db.Column(UnicodeText)

    # Competition time
    #
    # start_date has to be smaller or equal to end_date

    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=False)

    # Competition organizers and pilots

    admins = db.relationship('User', secondary=competition_admin_table)

    participants = db.relationship('CompetitionParticipation')

    # Metadata

    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    creator_id = db.Column(Integer, db.ForeignKey('tg_user.id', ondelete='SET NULL'))
    creator = db.relationship('User')

    # Location of the competition (optional)

    location = db.Column(Unicode(64))

    # Competition airport (optional)

    airport_id = db.Column(Integer, db.ForeignKey('airports.id', ondelete='SET NULL'))
    airport = db.relationship('Airport')

    # Competitions classes

    classes = db.relationship('CompetitionClass')

    ##############################

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Competition: id={} name=\'{}\'>' \
            .format(self.id, self.name).encode('utf-8')

    ##############################

    def is_writable(self, user):
        return user and \
            (user.is_manager() or user == self.creator or user in self.admins)

    ##############################

    @property
    def location_string(self):
        """ A string containing the location of the competition. """

        if self.location and len(self.location) != 0:
            return self.location

        if self.airport_id:
            return self.airport.name


class CompetitionParticipation(db.Model):
    """
    This table describes the many-to-many relationship between
    competitions and pilots and their type of relationship.

    Admins can change the details of the competition and add new pilots
    and other admins to the competition.
    """

    __tablename__ = 'competition_participation'
    __table_args__ = (
        db.UniqueConstraint(
            'competition_id', 'user_id', name='unique_participation'),
    )

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # The competition that this class definition belongs to

    competition_id = db.Column(
        Integer, db.ForeignKey('competitions.id', ondelete='CASCADE'),
        nullable=False)
    competition = db.relationship('Competition', innerjoin=True)

    # SkyLines user account

    user_id = db.Column(
        Integer, db.ForeignKey('tg_user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', innerjoin=True)

    # Competition class (optional)

    class_id = db.Column(
        Integer, db.ForeignKey('competition_classes.id', ondelete='SET NULL'))
    class_ = db.relationship('CompetitionClass')

    # Timestamps

    join_time = db.Column(DateTime)

    ##############################

    def __repr__(self):
        return '<CompetitionParticipation: id={}>' \
            .format(self.id).encode('utf-8')


class CompetitionClass(db.Model):
    """
    This table describes a competition class.

    The use of competition classes should be optional, for competitions
    that don't have classes.
    """

    __tablename__ = 'competition_classes'

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # The competition that this class definition belongs to

    competition_id = db.Column(
        Integer, db.ForeignKey('competitions.id', ondelete='CASCADE'),
        nullable=False)
    competition = db.relationship('Competition', innerjoin=True)

    # Name of the competition class

    name = db.Column(Unicode(64), nullable=False)

    # Description of the competition class (optional)

    description = db.Column(UnicodeText)

    # Competition class pilots

    participants = db.relationship('CompetitionParticipation')

    ##############################

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<CompetitionClass: id={} name=\'{}\'>' \
            .format(self.id, self.name).encode('utf-8')
