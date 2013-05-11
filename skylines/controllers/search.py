import shlex

from tg import expose
from tg.decorators import without_trailing_slash

from .base import BaseController
from skylines.model import User, Club, Airport
from skylines.model.search import combined_search_query, escape_tokens

MODELS = [User, Club, Airport]


class SearchController(BaseController):
    @without_trailing_slash
    @expose('search/list.jinja')
    def index(self, **kw):
        search_text = kw.get('text')
        if not search_text:
            return dict()

        # Split the search text into tokens and escape them properly
        tokens = shlex.split(search_text.encode('utf-8'))
        tokens = escape_tokens(tokens)

        # Create combined search query
        query = combined_search_query(MODELS, tokens)

        # Perform query and limit output to 20 items
        results = query.limit(20).all()

        return dict(search_text=search_text, results=results)
