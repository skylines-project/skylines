# -*- coding: utf-8 -*-
from skylines.lib.base import BaseController
from tg import expose, abort, config, redirect
from pylons import request
from string import split

__all__ = ['StaticResourceController']


class StaticResourceController(BaseController):
    @expose()
    def _default(self, *args, **kw):
        if not request.path.startswith(self.mount_point):
            abort(404)

        path = request.path[len(self.mount_point):].lstrip('/')
        path_components = split(path, '/', maxsplit = 1)
        if len(path_components) < 2:
            abort(404)

        module = path_components[0]
        path = path_components[1]

        # Check the config for the right redirection
        key = 'skylines.static.' + module
        value = config.get(key)

        # No redirection found -> 404 File not found
        if not value:
            abort(404)

        # Redirect to the static file
        redirect(value + path)
