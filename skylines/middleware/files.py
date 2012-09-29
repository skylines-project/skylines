from os.path import basename

from webob import Response
from webob.exc import HTTPNotFound, HTTPInternalServerError

from skylines.files import open_file
from skylines.middleware import PrefixHandlerMiddleware


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
