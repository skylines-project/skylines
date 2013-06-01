import operator

from flask.ext.babel import lazy_gettext as l_

from formencode import Schema, All
from formencode.validators import DateConverter, NotEmpty
from sprox.formbase import AddRecordForm, Field
from tw.forms import TextField

from .bootstrap import BootstrapForm
from .validators import FieldsOperatorValidator
from skylines.model import Competition


dates_validator = FieldsOperatorValidator(
    'start_date', 'end_date', operator.le,
    messages={
        'invalidNoMatch': l_('End date has to be after start date.')
    }
)


class NewForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __base_validator__ = Schema(chained_validators=[dates_validator])
    __model__ = Competition
    __limit_fields__ = ['name', 'start_date', 'end_date']
    __field_widget_args__ = {
        'name': dict(label_text=l_('Name')),
        'start_date': dict(label_text=l_('Start date'), help_text='dd.mm.yyyy'),
        'end_date': dict(label_text=l_('End date'), help_text='dd.mm.yyyy'),
    }

    name = TextField
    start_date = Field(TextField, All(
        NotEmpty, DateConverter(month_style='dd/mm/yyyy')))
    end_date = Field(TextField, All(
        NotEmpty, DateConverter(month_style='dd/mm/yyyy')))
