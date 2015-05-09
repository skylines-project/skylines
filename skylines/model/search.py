import shlex

from sqlalchemy import literal_column, cast, desc, Unicode
from sqlalchemy.dialects.postgresql import array

from skylines.database import db


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

    # Filter out id: tokens for later
    ids, tokens = process_id_option(tokens)

    # If there are still tokens left after id: token filtering
    if tokens:
        # Generate the search weight expression from the
        # searchable columns, tokens and patterns
        if not weight_func:
            weight_func = weight_expression

        weight = weight_func(columns, tokens)

    # If the search expression only included "special" tokens like id:
    else:
        weight = literal_column(str(1))

    # Create an array of stringified detail columns
    details = getattr(cls, '__search_detail_columns__', None)
    if details:
        details = [cast(getattr(cls, d), Unicode) for d in details]
    else:
        details = [literal_column('NULL')]

    # Create a query object
    query = db.session.query(
        cls_name.label('model'), cls.id.label('id'),
        cls.name.label('name'), array(details).label('details'),
        weight.label('weight'))

    # Filter out specific ids (optional)
    if ids:
        query = query.filter(cls.id.in_(ids))

    # Filter out results that don't match the patterns at all (optional)
    if not include_misses:
        query = query.filter(weight > 0)

    # Order by weight (optional)
    if ordered:
        query = query.order_by(desc(weight))

    return query

db.Model.search_query = classmethod(search_query)


def combined_search_query(models, tokens, include_misses=False, ordered=True):
    models, tokens = process_type_option(models, tokens)

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


def process_type_option(models, tokens):
    """
    This function looks for "type:<type>" in the tokens and filters the
    searchable models for the requested types.

    Returns the filtered list of models.
    """

    # Filter for type: and types: tokens
    types, new_tokens = __filter_prefixed_tokens('type', tokens)

    # Filter the list of models according to the type filter
    def in_types_list(model):
        return model.__name__.lower() in types

    new_models = filter(in_types_list, models)

    # Return original models list if there are no matching models
    if len(new_models) == 0:
        return models, new_tokens

    # Return filtered models and tokens
    return new_models, new_tokens


def process_id_option(tokens):
    """
    This function looks for "id:<id>" in the tokens, removes them from the
    token list and returns a list of ids.
    """

    # Filter for id: and ids: tokens
    ids, new_tokens = __filter_prefixed_tokens('id', tokens)

    # Convert ids to integers
    def int_or_none(value):
        try:
            return int(value)
        except ValueError:
            return None

    ids = filter(None, map(int_or_none, ids))

    # Return ids and tokens
    return ids, new_tokens


def __filter_prefixed_tokens(prefix, tokens):
    len_prefix = len(prefix)

    # The original tokens without the prefixed tokens
    new_tokens = []

    # The contents that were found after the prefixed tokens
    contents = []

    # Iterate through original tokens to find prefixed tokens
    for token in tokens:
        _token = token.lower()

        if _token.startswith(prefix + ':'):
            contents.append(_token[(len_prefix + 1):])

        elif _token.startswith(prefix + 's:'):
            contents.extend(_token[(len_prefix + 2):].split(','))

        else:
            new_tokens.append(token)

    # Strip whitespace from the types
    contents = map(str.strip, contents)

    return contents, new_tokens


def text_to_tokens(search_text):
    try:
        return shlex.split(search_text.encode('utf-8'))
    except ValueError:
        return search_text.split(' ')


def escape_tokens(tokens):
    # Escape % and _ properly
    tokens = [t.replace('%', '\\%').replace('_', '\\_') for t in tokens]

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
                weight *= len_token

                # Create the weighted ILIKE expression
                expression = column.weighted_ilike(token_pattern, weight)

                # Add the expression to list
                expressions.append(expression)

    return sum(expressions)


def process_result_details(models, results):
    models = {m.__name__: m for m in models}

    for result in results:
        model = models.get(result.model, None)
        if not model:
            continue

        details = getattr(model, '__search_detail_columns__', [None])
        if len(details) != len(result.details):
            continue

        for key, value in zip(details, result.details):
            if isinstance(key, str):
                setattr(result, key, value)
