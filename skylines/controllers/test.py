"""
Test Controller
"""

from tg import expose
from skylines.lib.base import BaseController


class TestController(BaseController):
    @expose('skylines.templates.test.index')
    def index(self):
        """Handle the front-page."""
        return dict(page = 'test')
