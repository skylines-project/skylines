from string import split

from webob.exc import HTTPFound, HTTPNotFound

from skylines.middleware import PrefixHandlerMiddleware


class StaticRedirectionMiddleware(PrefixHandlerMiddleware):
    def __init__(self, conf, mount_point = '/static'):
        PrefixHandlerMiddleware.__init__(self, mount_point)
        self.conf = conf

    def handle(self, path, environ, start_response):
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
