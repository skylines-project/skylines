#!/usr/bin/env python

import sys

from skylines import create_app
from skylines.model import User, Club, Airport
from skylines.model.search import combined_search_query, escape_tokens

MODELS = [User, Club, Airport]

app = create_app()
app.app_context().push()


def search_query(tokens):
    tokens = escape_tokens(tokens)
    return combined_search_query(MODELS, tokens)


tokens = sys.argv[1:]
for u in search_query(tokens).limit(20):
    model = globals()[u.model]
    instance = model.get(u.id)

    print u.weight, instance, u.details
