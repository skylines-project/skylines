from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from skylines.model import User, Club, Airport
from skylines.model.search import (
    combined_search_query, text_to_tokens, escape_tokens
)
from .json import jsonify

search_blueprint = Blueprint('search', 'skylines')

MODELS = [User, Club, Airport]

SEARCH_ARGS = {'q': fields.Str(required=True)}


@search_blueprint.route('/search')
@use_args(SEARCH_ARGS)
def index(args):
    search_text = args['q']

    # Split the search text into tokens and escape them properly
    tokens = text_to_tokens(search_text)
    tokens = escape_tokens(tokens)

    # Create combined search query
    query = combined_search_query(MODELS, tokens)

    # Perform query and limit output to 20 items
    results = query.limit(20).all()

    results = map(convert, results)

    return jsonify(results)


def convert(old):
    new = {'type': old[0].lower(), 'id': old[1], 'name': old[2]}

    if old[0] == 'User':
        pass

    elif old[0] == 'Club':
        new['website'] = old[3][0]

    elif old[0] == 'Airport':
        new['icao'] = old[3][0]
        new['frequency'] = old[3][1]

    return new
