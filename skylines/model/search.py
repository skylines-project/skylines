from sqlalchemy import literal_column, desc

from .session import DBSession


PATTERNS = [
    ('{}', 5),     # Matches token exactly
    ('{}%', 3),    # Begins with token
    ('% {}%', 2),  # Has token at word start
    ('%{}%', 1),   # Has token
]


def search_query(cls, tokens,
                 weight_func=None, include_misses=False, ordered=True):

    # Read the searchable columns from the table (strings)
    columns = cls.__searchable_columns__

    # Convert the columns from strings into column objects
    columns = [getattr(cls, c) for c in columns]

    # The model name that can be used to match search result to model
    cls_name = literal_column('\'{}\''.format(cls.__name__))

    # Generate the search weight expression from the
    # searchable columns, tokens and patterns
    if not weight_func:
        weight_func = weight_expression

    weight = weight_func(columns, tokens)

    # Create a query object
    query = DBSession.query(
        cls_name.label('model'), cls.id.label('id'),
        cls.name.label('name'), weight.label('weight'))

    # Filter out results that don't match the patterns at all (optional)
    if not include_misses:
        query = query.filter(weight > 0)

    # Order by weight (optional)
    if ordered:
        query = query.order_by(desc(weight))

    return query


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


def escape_tokens(tokens):
    # Escape % and _ properly
    tokens = [t.replace('%', '\%').replace('_', '\_') for t in tokens]

    # Use * as wildcard character
    tokens = [t.replace('*', '%') for t in tokens]

    return tokens


def weight_expression(columns, tokens):
    expressions = []

    # Use entire search string as additional token
    if len(tokens) > 1:
        tokens = tokens + [' '.join(tokens)]

    for column in columns:
        for token in tokens:
            len_token = len(token)

            for pattern, weight in PATTERNS:
                # Inject the token in the search pattern
                token_pattern = pattern.format(token)

                # Adjust the weight for the length of the token
                # (the long the matched token, the greater the weight)
                weight = weight * len_token

                # Create the weighted ILIKE expression
                expression = column.weighted_ilike(token_pattern, weight)

                # Add the expression to list
                expressions.append(expression)

    return sum(expressions)
