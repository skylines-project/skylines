from flask import make_response
from functools import wraps


class vary:
    def __init__(self, headers=None):
        self.headers = headers

    def __call__(self, view):
        @wraps(view)
        def decorated_view(*args, **kwargs):
            response = make_response(view(*args, **kwargs))
            response.headers['Vary'] = self.headers
            return response

        return decorated_view
