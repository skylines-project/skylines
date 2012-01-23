"""
Test Controller
"""

from tg import expose
from skylines.lib.base import BaseController
from skylines.lib.igc.parser import SimpleParser


class TestController(BaseController):
    @expose('skylines.templates.test.index')
    def index(self):
        """Handle the front-page."""
        return dict(page = 'test')

    @expose('skylines.templates.test.display_flight')
    def display_flight(self, igc_file):
        """Handle the flight display page."""
        parser = SimpleParser()
        fixes = parser.parse(igc_file.file)

        content = fixes
        return dict(page = 'test', content = content)
