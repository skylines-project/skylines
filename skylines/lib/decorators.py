from simplejson import dumps
from functools import wraps

from formencode import Schema, All, Invalid

from tg import response
from flask import request


def jsonp(func):
    def jsonp_handler(*args, **kw):
        if 'callback' in kw:
            response.content_type = 'application/javascript'
            return '{}({});'.format(kw.pop('callback'), dumps(func(*args, **kw)))
        else:
            response.content_type = 'application/json'
            return dumps(func(*args, **kw))

    return jsonp_handler


class validate:
    def __init__(self, form, errorhandler):
        self.form = form
        self.errorhandler = errorhandler

    def __call__(self, fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            try:
                self.form.validate(request.form)
            except Invalid:
                return self.errorhandler()
            else:
                return fn(*args, **kwargs)

        return decorated_view
