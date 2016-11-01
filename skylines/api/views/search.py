from flask import Blueprint, request

from skylines.api.json import jsonify
from skylines.model import User, Club, Airport
from skylines.model.search import (
    combined_search_query, text_to_tokens, escape_tokens,
    process_result_details
)

search_blueprint = Blueprint('search', 'skylines')

MODELS = [User, Club, Airport]


@search_blueprint.route('/search', strict_slashes=False)
def index():
    search_text = request.values.get('text', '').strip()
    if not search_text:
        return jsonify(results=[])

    return jsonify(results=search(search_text))


def search(text):
    # Split the search text into tokens and escape them properly
    tokens = text_to_tokens(text)
    tokens = escape_tokens(tokens)

    # Create combined search query
    query = combined_search_query(MODELS, tokens)

    # Perform query and limit output to 20 items
    results = query.limit(20).all()

    process_result_details(MODELS, results)

    results_json = []
    for r in results:
        result = {
            'type': r.model.lower(),
            'id': r.id,
            'name': r.name,
        }

        if hasattr(r, 'website') and r.website:
            result['website'] = r.website

        if hasattr(r, 'icao') and r.icao:
            result['icao'] = r.icao

        if hasattr(r, 'frequency') and r.frequency:
            result['frequency'] = '%.3f' % (float(r.frequency))

        results_json.append(result)

    return results_json
