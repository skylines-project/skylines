from flask import make_response
from functools import wraps, update_wrapper

def vary_accept(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Vary'] = 'accept'
        return response

    return update_wrapper(no_cache, view)
