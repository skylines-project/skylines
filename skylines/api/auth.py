from functools import wraps

from flask import g, request
from werkzeug.exceptions import Unauthorized

from skylines.model import User


def check():
    """
    Checks for the Authorization header, searches for the corresponding user,
    validates the password and saves the user to ``g.user``. If no user could
    be found or the password does not match it raises an ``Unauthorized``
    exception.

    :exception Unauthorized: if no user was found or the password is wrong
    """
    g.user = None

    auth = request.authorization
    if not auth:
        return

    user = User.by_email_address(auth.username)
    if not user or not user.validate_password(auth.password):
        raise Unauthorized('Please check your credentials.')

    g.user = user


def required(f):
    """
    Decorator that checks if ``g.user`` is set and raises an ``Unauthorized``
    exception otherwise.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user:
            return f(*args, **kwargs)
        else:
            raise Unauthorized('This part of the API requires authentication.')

    return decorated
