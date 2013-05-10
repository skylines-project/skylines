#!/usr/bin/python

import sys

from sqlalchemy import desc

from skylines.config import environment
from skylines import model

environment.load_from_file()

tokens = sys.argv[1:]


def search_query(tokens):
    # Escape % and _ properly
    tokens = [t.replace('%', '\%').replace('_', '\_') for t in tokens]

    # Use * as wildcard character
    tokens = [t.replace('*', '%') for t in tokens]

    q1 = model.User.search_query(tokens, ordered=False)
    q2 = model.Club.search_query(tokens, ordered=False)
    q3 = model.Airport.search_query(tokens, ordered=False)

    return q1.union(q2, q3).order_by(desc('weight'))

for u in search_query(tokens).limit(20):
    print u
