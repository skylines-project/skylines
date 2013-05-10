#!/usr/bin/python

import sys

from sqlalchemy import desc, literal_column

from skylines.config import environment
from skylines import model


NULL = literal_column(str(0))

environment.load_from_file()

tokens = sys.argv[1:]

session = model.DBSession


def get_query(type, model, query_attr, tokens):
    query_attr = getattr(model, query_attr)

    col_vals = []

    # Matches token exactly
    col_vals.extend([(query_attr, '{}'.format(token), len(token) * 5) for token in tokens])
    # Begins with token
    col_vals.extend([(query_attr, '{}%'.format(token), len(token) * 3) for token in tokens])
    # Has token at word start
    col_vals.extend([(query_attr, '% {}%'.format(token), len(token) * 2) for token in tokens])
    # Has token
    col_vals.extend([(query_attr, '%{}%'.format(token), len(token)) for token in tokens])

    weight = sum([col.weighted_ilike(val, rel) for col, val, rel in col_vals], NULL)

    # The search result type
    type = literal_column('\'{}\''.format(type))

    return session.query(type.label('type'),
                         model.id.label('id'),
                         query_attr.label('name'),
                         weight.label('weight')).filter(weight > NULL)


def search_query(tokens):
    if len(tokens) > 1:
        tokens.append(' '.join(tokens))

    q1 = get_query('user', model.User, 'name', tokens)
    q2 = get_query('club', model.Club, 'name', tokens)
    q3 = get_query('airport', model.Airport, 'name', tokens)

    return q1.union(q2, q3).order_by(desc('weight'))

for u in search_query(tokens).limit(20):
    print u
