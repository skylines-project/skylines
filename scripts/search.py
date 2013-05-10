#!/usr/bin/python

import sys

from sqlalchemy import case, desc, literal_column

from skylines.config import environment
from skylines import model


def ilike_as_int(column, value, relevance):
    # Make sure relevance is numeric and we can safely
    # pass it to the literal_column()
    assert isinstance(relevance, (int, float))

    # Convert relevance to a literal_column()
    relevance = literal_column(str(relevance))

    # Return case expression
    return case([(column.ilike(value), relevance)], else_=literal_column(str(0)))


def ilikes_as_int(col_vals):
    return sum([ilike_as_int(col, val, rel) for col, val, rel in col_vals], literal_column(str(0)))


environment.load_from_file()

tokens = sys.argv[1:]
if len(tokens) > 1:
    tokens.append(' '.join(tokens))

session = model.DBSession


def get_query(type, model, query_attr):
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

    relevance = ilikes_as_int(col_vals)

    # The search result type
    type = literal_column('\'{}\''.format(type))

    return session.query(type.label('type'),
                         model.id.label('id'),
                         query_attr.label('name'),
                         relevance.label('relevance')).filter(relevance > literal_column(str(0)))

q1 = get_query('user', model.User, 'display_name')
q2 = get_query('club', model.Club, 'name')
q3 = get_query('airport', model.Airport, 'name')

q = q1.union(q2, q3)

for u in q.order_by(desc('relevance')).limit(20):
    print u
