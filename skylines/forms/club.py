from flask.ext.babel import lazy_gettext as l_
from flask_wtf import Form

from sprox.widgets import PropertySingleSelectField
from wtforms import TextField, SelectField as _SelectField
from wtforms.validators import InputRequired, URL, ValidationError

from skylines import db
from skylines.model import Club


class SelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        query = db.session.query(Club.id, Club.name).order_by(Club.name)
        options = [(None, 'None')] + query.all()
        d['options'] = options
        return d

    def validate(self, value, *args, **kw):
        if isinstance(value, Club):
            value = value.id
        return super(SelectField, self).validate(value, *args, **kw)


class ClubsSelectField(_SelectField):
    def __init__(self, *args, **kwargs):
        super(ClubsSelectField, self).__init__(*args, **kwargs)
        self.coerce = int

    def process(self, *args, **kwargs):
        users = Club.query().order_by(Club.name)
        self.choices = [(0, '[' + l_('No club') + ']')]
        self.choices.extend([(user.id, user) for user in users])

        super(ClubsSelectField, self).process(*args, **kwargs)


class ChangeClubForm(Form):
    club = ClubsSelectField(l_('Club'))


class CreateClubForm(Form):
    name = TextField(l_('Name'), validators=[InputRequired()])

    def validate_name(form, field):
        if Club.exists(name=field.data):
            raise ValidationError(l_('A club with this name exists already.'))


class EditClubForm(Form):
    name = TextField(l_('Name'), validators=[InputRequired()])
    website = TextField(l_('Website'), validators=[URL()])

    def validate_name(form, field):
        if field.data == field.object_data:
            return

        if Club.exists(name=field.data):
            raise ValidationError(l_('A club with this name exists already.'))
