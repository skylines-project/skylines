import os

from webob import Response
from webob.exc import HTTPNotFound, HTTPInternalServerError

from skylines.middleware import PrefixHandlerMiddleware
import mimetypes


class AssetsMiddleware(PrefixHandlerMiddleware):
    """
    This middleware is only needed if the server is not statically
    serving the "webassets" folder
    """
    def __init__(self, conf):
        mount_point = conf['webassets.base_url']
        PrefixHandlerMiddleware.__init__(self, mount_point)

        self.base_dir = conf['webassets.base_dir']

    def handle(self, path, environ, start_response):
        try:
            path = os.path.join(self.base_dir, path)

            response = Response()

            content_type, _ = mimetypes.guess_type(path)
            if content_type:
                response.content_type = content_type

            response.body_file = file(path)
            return response(environ, start_response)
        except IOError:
            return HTTPNotFound()(environ, start_response)
        except:
            return HTTPInternalServerError()(environ, start_response)
