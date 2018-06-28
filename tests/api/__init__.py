import base64

from werkzeug.datastructures import Headers


def auth_for(user):
    return basic_auth(user.email_address, user.original_password)


def basic_auth(email, password):
    headers = Headers()
    hash_bytes = (email + u':' + password).encode('utf-8')
    basic_auth_hash = base64.b64encode(hash_bytes).decode('utf-8')
    headers.add(u'Authorization', u'Basic ' + basic_auth_hash)
    return headers
