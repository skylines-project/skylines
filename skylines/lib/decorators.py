from functools import wraps

from flask import current_app, request, flash, redirect, url_for
from flask.ext.login import current_user


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


class login_required:
    def __init__(self, msg=None):
        self.msg = msg

    def __call__(self, fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated():
                if self.msg:
                    flash(unicode(self.msg))

                return redirect(url_for('login', next=request.url))

            return fn(*args, **kwargs)
        return decorated_view
