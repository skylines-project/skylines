#!/usr/bin/python

import sys

from sqlalchemy import desc

from skylines.config import environment
from skylines import model

environment.load_from_file()

tokens = sys.argv[1:]


def combined_search_query(models, tokens, include_misses=False, ordered=True):
    # Build sub search queries
    queries = [model.search_query(
        tokens, include_misses=include_misses, ordered=False)
        for model in models]

    # Build combined search query
    query = queries[0]
    if len(queries) > 1:
        query = query.union(*queries[1:])

    # Order by weight (optional)
    if ordered:
        query = query.order_by(desc('weight'))

    return query


def search_query(tokens):
    # Escape % and _ properly
    tokens = [t.replace('%', '\%').replace('_', '\_') for t in tokens]

    # Use * as wildcard character
    tokens = [t.replace('*', '%') for t in tokens]

    models = [model.User, model.Club, model.Airport]

    return combined_search_query(models, tokens)


for u in search_query(tokens).limit(20):
    print u
