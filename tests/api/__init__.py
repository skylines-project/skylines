import base64

from werkzeug.datastructures import Headers


def basic_auth(email, password):
    headers = Headers()
    headers.add('Authorization', 'Basic ' + base64.b64encode(email + ':' + password))
    return headers
