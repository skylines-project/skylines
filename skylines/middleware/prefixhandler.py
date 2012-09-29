from webob.exc import HTTPNotFound


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
