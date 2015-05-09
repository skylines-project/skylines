from wtforms.validators import ValidationError
from sqlalchemy.sql.expression import or_

from skylines.database import db
from skylines.model import Flight


class CompareTo(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param cmp:
        Compare function that takes two parameters: own value and other value
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """

    DEFAULT_ERROR_MSG = 'Field must be equal to %(other_name)s.'

    def __init__(self, fieldname, cmp=(lambda x, y: x == y), message=None):
        self.fieldname = fieldname
        self.cmp = cmp
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if not self.cmp(field.data, other.data):
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = self.message
            if message is None:
                message = field.gettext(self.DEFAULT_ERROR_MSG)

            raise ValidationError(message % d)


class NotEqualTo(CompareTo):
    DEFAULT_ERROR_MSG = 'Field must not be equal to %(other_name)s.'

    def __init__(self, *args, **kw):
        super(NotEqualTo, self).__init__(*args, cmp=(lambda x, y: x != y), **kw)


class CheckPilot(object):
    """
    Checks if the pilot/co-pilot is airborne already with another flight.

    :param flight_id_field:
        The flight id field inside the current form.
    """

    def __init__(self, flight_id_field, message=None):
        self.flight_id_field = flight_id_field
        self.message = message

    def __call__(self, form, field):
        try:
            flight = form[self.flight_id_field]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)

        cte = db.session.query(Flight).filter(Flight.id == flight.data).cte()

        count = db.session.query(Flight) \
                  .filter(Flight.id != flight.data) \
                  .filter(Flight.landing_time >= cte.c.takeoff_time) \
                  .filter(Flight.takeoff_time <= cte.c.landing_time) \
                  .filter(or_(Flight.pilot_id == field.data, Flight.co_pilot_id == field.data)) \
                  .count()

        if count:
            message = self.message
            if message is None:
                message = field.gettext(self.DEFAULT_ERROR_MSG)

            raise ValidationError(message)
