from marshmallow.validate import *  # NOQA
from marshmallow.validate import Validator, ValidationError


class NotEmpty(Validator):
    def __call__(self, value):
        if len(value) == 0:
            raise ValidationError("Must not be empty.")


class EmptyOr(Validator):
    def __init__(self, other_validator):
        self.other_validator = other_validator

    def __call__(self, value):
        if len(value) != 0:
            self.other_validator(value)
