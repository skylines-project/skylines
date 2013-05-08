from tg.i18n import lazy_ugettext as l_

from sprox.formbase import AddRecordForm

from .bootstrap import BootstrapForm
from skylines.model import Competition


class NewForm(AddRecordForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Competition
    __limit_fields__ = ['name', 'start_date', 'end_date']
    __field_widget_args__ = {
        'name': dict(label_text=l_('Name')),
        'start_date': dict(label_text=l_('Start date')),
        'end_date': dict(label_text=l_('End date')),
    }
