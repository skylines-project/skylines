from werkzeug.datastructures import Headers

from skylines.lib.basic_auth import encode as basic_auth_encode


def auth_for(user):
    return basic_auth(user.email_address, user.original_password)


def basic_auth(email, password):
    headers = Headers()
    headers.add("Authorization", basic_auth_encode(email, password))
    return headers
