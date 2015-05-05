from collections import OrderedDict

from marshmallow import Schema as _Schema, fields, post_dump


class Schema(_Schema):
    class Meta:
        ordered = True


def replace_keywords(data):
    return OrderedDict(map(strip_underscore, data.iteritems()))


def strip_underscore(kv):
    k, v = kv
    if k.startswith('_'):
        k = k[1:]

    return k, v


class AirspaceSchema(Schema):
    name = fields.String()
    _class = fields.String(attribute='airspace_class')
    top = fields.String()
    base = fields.String()
    country = fields.String(attribute='country_code')

    @post_dump
    def replace_keywords(self, data):
        return replace_keywords(data)

airspace_list_schema = AirspaceSchema()
