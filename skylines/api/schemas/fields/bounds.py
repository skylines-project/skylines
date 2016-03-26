from marshmallow import fields
from webargs import ValidationError

from skylines.model import Bounds


class BoundsField(fields.Field):
    def _deserialize(self, value, attr, data):
        try:
            return Bounds.from_bbox_string(value)
        except ValueError as e:
            raise ValidationError(e.message)
