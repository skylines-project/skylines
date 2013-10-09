from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from skylines.forms.pilot import ClubPilotsSelectField


class ChangePilotsForm(Form):
    pilot_id = ClubPilotsSelectField(l_('Pilot'))
    co_pilot_id = ClubPilotsSelectField(l_('Co-Pilot'))
