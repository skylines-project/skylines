# -*- coding: utf-8 -*-

class RootPrefixMiddleware(object):
    """This filter class is a kludge to allow the Skylines application
    to be mounted at the very root of a web server when using FastCGI.
    It adjusts the variables SCRIPT_NAME and PATH_INFO.  This is
    necessary because lighttpd uses the first URI component as
    SCRIPT_NAME, which confuses TurboGears."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # clear SCRIPT_NAME
        environ['SCRIPT_NAME'] = ''

        # PATH_INFO is the full request URI without the query string
        uri = environ['REQUEST_URI']
        q = uri.find('?')
        if q >= 0:
            path_info = uri[:q]
        else:
            path_info = uri
        # kill multiple slashes at the beginning, which would lead to
        # endless redirects
        path_info = '/' + path_info.lstrip('/')
        environ['PATH_INFO'] = path_info

        return self.app(environ, start_response)

def make_root_prefix_middleware(app, global_conf):
    return RootPrefixMiddleware(app)

