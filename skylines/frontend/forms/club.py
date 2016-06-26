from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from wtforms import TextField, SelectField
from wtforms.validators import InputRequired, URL, ValidationError, Optional

from skylines.model import Club


class EditClubForm(Form):
    name = TextField(l_('Name'), validators=[InputRequired()])
    website = TextField(l_('Website'), validators=[Optional(), URL()])

    def validate_name(form, field):
        if field.data == field.object_data:
            return

        if Club.exists(name=field.data):
            raise ValidationError(l_('A club with this name exists already.'))
