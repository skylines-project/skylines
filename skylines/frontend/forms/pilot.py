from flask import g
from flask.ext.babel import lazy_gettext as l_, ngettext
from flask_wtf import Form

from wtforms import (
    TextField, SelectField, PasswordField, BooleanField, HiddenField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Length, EqualTo, InputRequired, Email, ValidationError
)

from skylines.model import User
from .units import (
    UnitsPresetSelectField, DistanceUnitSelectField, AltitudeUnitSelectField,
    LiftUnitSelectField, SpeedUnitSelectField
)
from .select import GroupSelectField


class ClubPilotsSelectField(GroupSelectField):
    def __init__(self, *args, **kwargs):
        super(ClubPilotsSelectField, self).__init__(*args, **kwargs)
        self.coerce = int

    def process(self, *args, **kwargs):
        self.choices = [
            (0, '[' + l_('Unknown or other person') + ']'),
            (g.current_user.id, g.current_user.name),
        ]

        club = g.current_user.club
        if club:
            members = User.query(club_id=club.id) \
                .order_by(User.name) \
                .filter(User.id != g.current_user.id)

            members = [(member.id, member.name) for member in members]

            self.choices.append((club.name, members))

        super(ClubPilotsSelectField, self).process(*args, **kwargs)


class ChangePasswordForm(Form):
    current_password = PasswordField(l_('Current Password'))
    password = PasswordField(l_('Password'), validators=[
        Length(min=6, message=l_('Your password must have at least 6 characters.')),
    ])
    verify_password = PasswordField(l_('Verify Password'), validators=[
        EqualTo('password', message=l_('Your passwords do not match.')),
    ])


class CreateClubPilotForm(Form):
    email_address = EmailField(l_('Email Address'), validators=[
        InputRequired(message=l_('Please enter your email address.')),
        Email(),
    ])
    first_name = TextField(l_('First Name'), validators=[
        InputRequired(message=l_('Please enter your first name.')),
    ])
    last_name = TextField(l_('Last Name'), validators=[
        InputRequired(message=l_('Please enter your last name.')),
    ])

    def validate_email_address(form, field):
        if User.exists(email_address=field.data):
            raise ValidationError(l_('A pilot with this email address exists already.'))


class CreatePilotForm(CreateClubPilotForm, ChangePasswordForm):
    # email_address, name from CreateClubPilotForm
    # password, verify_password from ChangePasswordForm
    pass


class TrackingDelaySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(TrackingDelaySelectField, self).__init__(*args, **kwargs)

        self.coerce = int
        self.choices = [(0, l_('None'))]
        for x in range(1, 10) + range(10, 30, 5) + range(30, 61, 15):
            self.choices.append((x, ngettext(u'%(num)u minute', u'%(num)u minutes', x)))


class EditPilotForm(Form):
    email_address = EmailField(l_('Email Address'), validators=[
        InputRequired(message=l_('Please enter your email address.')),
        Email(),
    ])
    first_name = TextField(l_('First Name'), validators=[
        InputRequired(message=l_('Please enter your first name.')),
    ])
    last_name = TextField(l_('Last Name'), validators=[
        InputRequired(message=l_('Please enter your last name.')),
    ])
    unit_preset = UnitsPresetSelectField(l_('Unit Preset'))
    distance_unit = DistanceUnitSelectField(l_('Distance Unit'))
    speed_unit = SpeedUnitSelectField(l_('Speed Unit'))
    lift_unit = LiftUnitSelectField(l_('Lift Unit'))
    altitude_unit = AltitudeUnitSelectField(l_('Altitude Unit'))

    def validate_email_address(form, field):
        if field.data == field.object_data:
            return

        if User.exists(email_address=field.data):
            raise ValidationError(l_('A pilot with this email address exists already.'))


class LiveTrackingSettingsForm(Form):
    tracking_delay = TrackingDelaySelectField(l_('Tracking Delay'))
    tracking_callsign = TextField(l_('Tracking Callsign'), validators=[
        Length(max=5, message=l_('Your callsign must not have more than 5 characters.')),
    ])


class RecoverStep1Form(Form):
    email_address = EmailField(l_('Email Address'), validators=[
        InputRequired(message=l_('Please enter your email address.')),
        Email(),
    ])

    def validate_email_address(form, field):
        if not User.exists(email_address=field.data):
            raise ValidationError(l_('There is no pilot with this email address.'))


class RecoverStep2Form(ChangePasswordForm):
    key = HiddenField()


class LoginForm(Form):
    email_address = EmailField(l_('Email Address'), validators=[
        InputRequired(message=l_('Please enter your email address.')),
        Email(),
    ])
    password = PasswordField(l_('Password'), validators=[
        InputRequired(message=l_('Please enter your password.')),
    ])
    remember_me = BooleanField(l_('Remember me'))
