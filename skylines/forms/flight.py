from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from wtforms import TextField
from wtforms.validators import Length

from skylines.forms.pilot import ClubPilotsSelectField
from skylines.forms.aircraft_model import AircraftModelSelectField


class ChangePilotsForm(Form):
    pilot_id = ClubPilotsSelectField(l_('Pilot'))
    co_pilot_id = ClubPilotsSelectField(l_('Co-Pilot'))


class ChangeAircraftForm(Form):
    model_id = AircraftModelSelectField(l_('Aircraft Model'))
    registration = TextField(l_('Aircraft Registration'), validators=[
        Length(max=32),
    ])
    competition_id = TextField(l_('Competition Number'), validators=[
        Length(max=5),
    ])
