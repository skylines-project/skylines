from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from wtforms import TextField
from wtforms.validators import Length
from wtforms.fields import IntegerField
from wtforms.widgets import HiddenInput

from .pilot import ClubPilotsSelectField
from .aircraft_model import AircraftModelSelectField
from .validators import CompareTo, CheckPilot


class FlightForm(Form):
    id = IntegerField(widget=HiddenInput())


class ChangePilotsForm(FlightForm):
    pilot_id = ClubPilotsSelectField(l_('Pilot'), validators=[
        CheckPilot('id', message=l_('Pilot is already airborne in another flight.')),
    ])
    pilot_name = TextField(l_(u'Pilot name'))
    co_pilot_id = ClubPilotsSelectField(l_('Co-Pilot'), validators=[
        CompareTo(
            'pilot_id',
            cmp=(lambda x, y: x == 0 or x != y),
            message=l_('Pilot and co-pilot can not be the same person.')
        ),
        CheckPilot('id', message=l_('Co-Pilot is already airborne in another flight.')),
    ])
    co_pilot_name = TextField(l_(u'Co-Pilot name'))


class ChangeAircraftForm(FlightForm):
    model_id = AircraftModelSelectField(l_('Aircraft Model'))
    registration = TextField(l_('Aircraft Registration'), validators=[
        Length(max=32),
    ])
    competition_id = TextField(l_('Competition Number'), validators=[
        Length(max=5),
    ])
