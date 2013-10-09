from flask import g
from flask.ext.babel import lazy_gettext as l_, ngettext
from flask_wtf import Form

from wtforms import (
    TextField as _TextField, SelectField, PasswordField, BooleanField
)
from wtforms.validators import (
    Length, EqualTo, InputRequired, Email, ValidationError
)

from skylines.model import User
from skylines.forms import units
from skylines.forms.club import ClubsSelectField


class ClubPilotsSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(ClubPilotsSelectField, self).__init__(*args, **kwargs)
        self.coerce = int

    def process(self, *args, **kwargs):
        users = User.query(club_id=g.current_user.club_id).order_by(User.name)
        self.choices = [(0, '[unspecified]')]
        self.choices.extend([(user.id, user) for user in users])

        super(ClubPilotsSelectField, self).process(*args, **kwargs)


class ChangePasswordForm(Form):
    password = PasswordField(l_('Password'), validators=[
        Length(min=6),
    ])
    verify_password = PasswordField(l_('Verify Password'), validators=[
        EqualTo('password', message=l_('Passwords do not match')),
    ])


class CreateClubPilotForm(Form):
    email_address = _TextField(l_('eMail Address'), validators=[
        InputRequired(),
        Email(),
    ])
    name = _TextField(l_('Name'), validators=[
        InputRequired(),
    ])

    def validate_email_address(form, field):
        if User.exists(email_address=field.data):
            raise ValidationError(l_('A pilot with this email address exists already.'))


class CreatePilotForm(CreateClubPilotForm, ChangePasswordForm):
    # email_address, name from CreateClubPilotForm
    # password, verify_password from ChangePasswordForm
    club_id = ClubsSelectField(l_('Club'))


class TrackingDelaySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(TrackingDelaySelectField, self).__init__(*args, **kwargs)

        self.coerce = int
        self.choices = [(0, l_('None'))]
        for x in range(1, 10) + range(10, 30, 5) + range(30, 61, 15):
            self.choices.append((x, ngettext(u'%(num)u minute', u'%(num)u minutes', x)))


class EditPilotForm(Form):
    email_address = _TextField(l_('eMail Address'), validators=[
        InputRequired(),
        Email(),
    ])
    name = _TextField(l_('Name'), validators=[
        InputRequired(),
    ])
    tracking_delay = TrackingDelaySelectField(l_('Tracking Delay'))
    unit_preset = units.PresetSelectField(l_('Unit Preset'))
    distance_unit = units.DistanceSelectField(l_('Distance Unit'))
    speed_unit = units.SpeedSelectField(l_('Speed Unit'))
    lift_unit = units.LiftSelectField(l_('Lift Unit'))
    altitude_unit = units.AltitudeSelectField(l_('Altitude Unit'))
    eye_candy = BooleanField(l_('Eye Candy'))

    def validate_email_address(form, field):
        if field.data == field.object_data:
            return

        if User.exists(email_address=field.data):
            raise ValidationError(l_('A pilot with this email address exists already.'))
