from tg import expose
from tg.decorators import without_trailing_slash

from .base import BaseController
from skylines.model import User, Club, Airport
from skylines.model.search import (
    combined_search_query, text_to_tokens, escape_tokens,
    process_result_details
)

MODELS = [User, Club, Airport]


class SearchController(BaseController):
    @without_trailing_slash
    @expose('search/list.jinja')
    def index(self, **kw):
        search_text = kw.get('text')
        if not search_text:
            return dict()

        # Split the search text into tokens and escape them properly
        tokens = text_to_tokens(search_text)
        tokens = escape_tokens(tokens)

        # Create combined search query
        query = combined_search_query(MODELS, tokens)

        # Perform query and limit output to 20 items
        results = query.limit(20).all()

        process_result_details(MODELS, results)

        return dict(search_text=search_text, results=results)
