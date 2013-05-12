import operator

from tg.i18n import ugettext as _

from formencode import Invalid
from formencode.validators import FormValidator


class FieldsOperatorValidator(FormValidator):
    """
    Tests that the given two fields are in the right relation to each other.
    The values of both fields are passed to the operator function, which
    determines if the fields are okay or not.

    ::

        >>> f = FieldsOperatorValidator('start', 'end', operator.le)
        >>> f.to_python({'start': 3, 'end': 1})
        Traceback (most recent call last):
            ...
        Invalid: Fields do not match operator
    """

    operator = operator.eq
    field1 = None
    field2 = None

    __unpackargs__ = ('field1', 'field2', 'operator')

    messages = {
        'invalidNoMatch': _('Fields do not match operator'),
    }

    def __init__(self, *args, **kw):
        super(FieldsOperatorValidator, self).__init__(*args, **kw)

        if not (self.field1 and self.field2):
            raise TypeError(
                'FieldsOperatorValidator() requires at least two field names')

    def validate_python(self, field_dict, state):
        if (self.field1 in field_dict and self.field2 in field_dict and
            not self.operator(field_dict[self.field1],
                              field_dict[self.field2])):

            error_message = self.message('invalidNoMatch', state)
            raise Invalid(error_message, field_dict, state)
