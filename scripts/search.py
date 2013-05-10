#!/usr/bin/python

import sys

from skylines.config import environment
from skylines.model import User, Club, Airport
from skylines.model.search import combined_search_query, escape_tokens


def search_query(tokens):
    tokens = escape_tokens(tokens)
    models = [User, Club, Airport]
    return combined_search_query(models, tokens)


environment.load_from_file()

tokens = sys.argv[1:]
for u in search_query(tokens).limit(20):
    print u
