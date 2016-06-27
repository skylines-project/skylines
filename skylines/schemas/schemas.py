from marshmallow import Schema

from . import fields, validate


class ClubSchema(Schema):
    name = fields.String(required=True, strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
