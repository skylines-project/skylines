from webob.exc import HTTPFound, HTTPNotFound
from string import split


class StaticRedirectionMiddleware(object):
    """WSGI middleware for login clean-up."""

    def __init__(self, conf, mount_point = '/static'):
        self.conf = conf
        self.mount_point = mount_point

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if not path_info.startswith(self.mount_point):
            return HTTPNotFound()(environ, start_response)

        path = path_info[len(self.mount_point):].lstrip('/')
        path_components = split(path, '/', maxsplit = 1)
        if len(path_components) < 2:
            return HTTPNotFound()(environ, start_response)

        module = path_components[0]
        path = path_components[1]

        # Check the config for the right redirection
        key = 'skylines.static.' + module
        value = self.conf.get(key)

        # No redirection found -> 404 File not found
        if not value:
            return HTTPNotFound()(environ, start_response)

        location = value + path
        return HTTPFound(location=location)(environ, start_response)
