from werkzeug.exceptions import MethodNotAllowed


class HTTPMethodOverrideMiddleware(object):
    allowed_methods = frozenset([
        'GET',
        'HEAD',
        'POST',
        'DELETE',
        'PUT',
        'PATCH',
        'OPTIONS'
    ])

    bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()

        if method in self.allowed_methods:
            method = method.encode('ascii', 'replace')
            environ['REQUEST_METHOD'] = method
        elif method != '':
            return MethodNotAllowed(self.allowed_methods)(environ, start_response)

        if method in self.bodyless_methods:
            environ['CONTENT_LENGTH'] = '0'

        return self.app(environ, start_response)
