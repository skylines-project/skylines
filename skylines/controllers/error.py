# -*- coding: utf-8 -*-
"""Error controller"""

import re

from tg import request, expose
from tg.i18n import ugettext as _
from webob.exc import HTTPNotFound

from .base import BaseController
from skylines.model.session import DBSession

__all__ = ['ErrorController']

re_message = re.compile(r'</h1>(.+)</body>', re.DOTALL)


class ErrorController(BaseController):
    """
    Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.

    """

    @expose('generic/page.jinja')
    def document(self, *args, **kwargs):
        """Render the error document"""

        # Merge the user into the current DBSession
        # to prevent DetachedInstanceError
        if request.identity is not None:
            request.identity['user'] = DBSession.merge(request.identity['user'])

        resp = request.environ.get('pylons.original_response')
        if resp is None:
            raise HTTPNotFound

        match = re.search(re_message, resp.body)
        if match is not None:
            default_message = '<p>{}</p>'.format(match.group(1).strip())
        else:
            default_message = ("<p>We're sorry but we weren't able to process "
                               " this request.</p>")

        code = request.params.get('code', resp.status_int)
        title = _('Error {code}').format(code=code)

        values = dict(prefix=request.environ.get('SCRIPT_NAME', ''),
                      title=title,
                      content=request.params.get('message', default_message))
        return values
