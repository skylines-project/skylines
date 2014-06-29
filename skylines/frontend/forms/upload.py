from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form
from flask_wtf.file import FileRequired

from wtforms import TextField
from wtforms.fields import DateTimeField, BooleanField
from wtforms.validators import Required

from .file import MultiFileField
from .pilot import ClubPilotsSelectField
from .flight import ChangeAircraftForm, ChangePilotsForm
from .validators import CompareTo


class UploadForm(Form):
    file = MultiFileField(l_(u'IGC or ZIP file(s)'), validators=(
        FileRequired(l_('Please add one or more IGC or ZIP files')),
    ))
    pilot = ClubPilotsSelectField(l_(u'Pilot'))
    pilot_name = TextField(l_(u'Pilot name'))


class UploadUpdateForm(ChangeAircraftForm, ChangePilotsForm):
    takeoff_time = DateTimeField(l_('Takeoff'), format='%Y-%m-%d %H:%M:%S')

    scoring_start_time = DateTimeField(l_('Scoring Start Time'), validators=[
        CompareTo(
            'takeoff_time',
            cmp=(lambda x, y: x >= y),
            message=l_('Scoring Start Time must be after takeoff')
        )
    ], format='%Y-%m-%d %H:%M:%S')

    scoring_end_time = DateTimeField(l_('Scoring End Time'), validators=[
        CompareTo(
            'scoring_start_time',
            cmp=(lambda x, y: x >= y),
            message=l_('Scoring End Time must be after scoring start time')
        )
    ], format='%Y-%m-%d %H:%M:%S')

    landing_time = DateTimeField(l_('Landing Time'), validators=[
        CompareTo(
            'scoring_end_time',
            cmp=(lambda x, y: x >= y),
            message=l_('Landing Time must be after scoring end time')
        )
    ], format='%Y-%m-%d %H:%M:%S')

    airspace_usage = BooleanField(l_('Confirm airspace usage'), validators=[
        Required(message=l_('Please confirm you were allowed to use those airspaces'))
    ])
