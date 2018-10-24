from base64 import b64encode

from skylines.lib.types import is_unicode


def encode(name, password):
    if is_unicode(name):
        name = name.encode("utf-8")

    if is_unicode(password):
        password = password.encode("utf-8")

    return u"Basic " + b64encode(name + b":" + password).decode("ascii")
