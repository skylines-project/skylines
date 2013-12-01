from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from wtforms import TextField
from wtforms.validators import Length

from skylines.forms.pilot import ClubPilotsSelectField
from skylines.forms.aircraft_model import AircraftModelSelectField
from skylines.forms.validators import CompareTo


class ChangePilotsForm(Form):
    pilot_id = ClubPilotsSelectField(l_('Pilot'))
    pilot_name = TextField(l_(u'Pilot name'))
    co_pilot_id = ClubPilotsSelectField(l_('Co-Pilot'), validators=[
        CompareTo(
            'pilot_id',
            cmp=(lambda x, y: x == 0 or x != y),
            message=l_('Pilot and co-pilot can not be the same person.')
        ),
    ])
    co_pilot_name = TextField(l_(u'Co-Pilot name'))


class ChangeAircraftForm(Form):
    model_id = AircraftModelSelectField(l_('Aircraft Model'))
    registration = TextField(l_('Aircraft Registration'), validators=[
        Length(max=32),
    ])
    competition_id = TextField(l_('Competition Number'), validators=[
        Length(max=5),
    ])
