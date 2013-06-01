from flask.ext.babel import lazy_gettext as l_

from skylines.lib.validators import FileFieldValidator

from . import pilot
from .bootstrap import BootstrapForm
from .file import MultiFileField


file_field_validator = FileFieldValidator(
    not_empty=True,
    messages=dict(empty=l_("Please add one or more IGC or ZIP files")),
    accept_iterator=True
)

file_field = MultiFileField(
    'file', label_text=l_("IGC or ZIP file(s)"), validator=file_field_validator)

form = BootstrapForm('upload_form', submit_text="Upload", children=[
    file_field,
    pilot.SelectField('pilot', label_text=l_("Pilot"))
])
