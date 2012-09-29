from os.path import basename
from webob import Response
from webob.exc import HTTPFound, HTTPNotFound, HTTPInternalServerError
from string import split
from skylines.files import open_file


class PrefixHandlerMiddleware(object):
    def __init__(self, mount_point):
        self.mount_point = mount_point

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if not path_info.startswith(self.mount_point):
            return HTTPNotFound()(environ, start_response)

        path = path_info[len(self.mount_point):].lstrip('/')
        return self.handle(path, environ, start_response)

    def handle(self, path, environ, start_response):
        pass


class FilesMiddleware(PrefixHandlerMiddleware):
    def __init__(self, conf, mount_point = '/files'):
        PrefixHandlerMiddleware.__init__(self, mount_point)
        self.conf = conf

    def handle(self, path, environ, start_response):
        try:
            filename = basename(path)

            response = Response()
            response.content_type = 'text/x-igc'
            response.headerlist.append(('Content-Disposition',
                                        'attachment;filename={}'.format(filename)))
            response.body_file = open_file(filename)
            return response(environ, start_response)
        except IOError:
            return HTTPNotFound()(environ, start_response)
        except:
            return HTTPInternalServerError()(environ, start_response)


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
