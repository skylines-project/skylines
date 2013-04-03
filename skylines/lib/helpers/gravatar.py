import urllib
import hashlib


def get_url(email, size=100, default='mm'):
    if email is None:
        email = ''

    gravatar_url = "http://www.gravatar.com/avatar/"
    gravatar_url += hashlib.md5(email.lower().encode("utf8")).hexdigest()
    gravatar_url += "?" + urllib.urlencode({'d': default, 's': str(size)})
    return gravatar_url
