from collections import OrderedDict

from marshmallow import Schema


class BaseSchema(Schema):
    class Meta:
        ordered = True


def replace_keywords(data):
    return OrderedDict(map(strip_underscore, data.iteritems()))


def strip_underscore(kv):
    k, v = kv
    if k.startswith('_'):
        k = k[1:]

    return k, v
