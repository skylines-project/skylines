from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form
from flask_wtf.file import FileRequired

from wtforms import TextField

from .file import MultiFileField
from .pilot import ClubPilotsSelectField


class UploadForm(Form):
    file = MultiFileField(l_(u'IGC or ZIP file(s)'), validators=(
        FileRequired(l_('Please add one or more IGC or ZIP files')),
    ))
    pilot = ClubPilotsSelectField(l_(u'Pilot'))
    pilot_name = TextField(l_(u'Pilot name'))
