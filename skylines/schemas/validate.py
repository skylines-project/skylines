from marshmallow.validate import *  # NOQA


class NotEmpty(Validator):
    def __call__(self, value):
        if len(value) == 0:
            raise ValidationError('Must not be empty.')
