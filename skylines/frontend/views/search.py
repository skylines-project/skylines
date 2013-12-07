from flask import Blueprint, request, render_template

from skylines.model import User, Club, Airport
from skylines.model.search import (
    combined_search_query, text_to_tokens, escape_tokens,
    process_result_details
)

search_blueprint = Blueprint('search', 'skylines')

MODELS = [User, Club, Airport]


@search_blueprint.route('/')
def index():
    search_text = request.values.get('text', '').strip()
    if not search_text:
        return render_template('search/list.jinja')

    # Split the search text into tokens and escape them properly
    tokens = text_to_tokens(search_text)
    tokens = escape_tokens(tokens)

    # Create combined search query
    query = combined_search_query(MODELS, tokens)

    # Perform query and limit output to 20 items
    results = query.limit(20).all()

    process_result_details(MODELS, results)

    return render_template('search/list.jinja',
                           search_text=search_text,
                           results=results)
