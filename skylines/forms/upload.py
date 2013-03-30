from tg.i18n import lazy_ugettext as l_
from tw.forms.validators import FieldStorageUploadConverter
from skylines.forms import BootstrapForm, MultiFileField, pilot


file_field_validator = FieldStorageUploadConverter(
    not_empty=True,
    messages=dict(empty=l_("Please add one or more IGC or ZIP files")),
    accept_iterator=True
)

file_field = MultiFileField(
    'file', label_text=l_("IGC or ZIP file(s)"), validator=file_field_validator)

form = BootstrapForm('upload_form', submit_text="Upload", action='do', children=[
    file_field,
    pilot.SelectField('pilot', label_text=l_("Pilot"))
])
