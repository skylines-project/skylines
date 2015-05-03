from skylines.model import User, Club, Airport
from skylines.model.search import (
    combined_search_query, escape_tokens, text_to_tokens
)

MODELS = [User, Club, Airport]


def search(text):
    # Split the search text into tokens and escape them properly
    tokens = text_to_tokens(text)
    tokens = escape_tokens(tokens)

    # Create combined search query
    return combined_search_query(MODELS, tokens)


def test_tokenizer():
    # Check that this does not throw exceptions
    text_to_tokens('\\')
    text_to_tokens('blabla \\')
    text_to_tokens('"')
    text_to_tokens('"blabla \\')

    # Check that the tokenizer returns expected results
    assert text_to_tokens('a b c') == ['a', 'b', 'c']
    assert text_to_tokens('a \'b c\'') == ['a', 'b c']
    assert text_to_tokens('a "b c" d') == ['a', 'b c', 'd']
    assert text_to_tokens('old "mac donald" has a FARM') == \
        ['old', 'mac donald', 'has', 'a', 'FARM']


def test_escaping():
    assert escape_tokens(['hello!']) == ['hello!']
    assert escape_tokens(['hello *!']) == ['hello %!']
    assert escape_tokens(['hello %!']) == ['hello \\%!']
    assert escape_tokens(['hello _!']) == ['hello \\_!']


def test_search(test_user, test_admin):
    assert search('example').count() == 2
    assert search('user').count() == 1
    assert search('man').count() == 1
    assert search('man*er').count() == 1
    assert search('*er').count() == 2
    assert search('exa*er').count() == 2
    assert search('exp*er').count() == 0
    assert search('xyz').count() == 0
