from nose.tools import eq_

from skylines import db
from skylines.model import User, Club, Airport
from skylines.model.search import (
    combined_search_query, escape_tokens, text_to_tokens
)
from tests.data.bootstrap import bootstrap

MODELS = [User, Club, Airport]


def setup():
    # Add sample data to the database
    bootstrap()


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
    eq_(text_to_tokens('a b c'), ['a', 'b', 'c'])
    eq_(text_to_tokens('a \'b c\''), ['a', 'b c'])
    eq_(text_to_tokens('a "b c" d'), ['a', 'b c', 'd'])
    eq_(text_to_tokens('old "mac donald" has a FARM'),
        ['old', 'mac donald', 'has', 'a', 'FARM'])


def test_escaping():
    eq_(escape_tokens(['hello!']), ['hello!'])
    eq_(escape_tokens(['hello *!']), ['hello %!'])
    eq_(escape_tokens(['hello %!']), ['hello \\%!'])
    eq_(escape_tokens(['hello _!']), ['hello \\_!'])


def test_search():
    eq_(search('example').count(), 2)
    eq_(search('user').count(), 1)
    eq_(search('man').count(), 1)
    eq_(search('man*er').count(), 1)
    eq_(search('*er').count(), 2)
    eq_(search('exa*er').count(), 2)
    eq_(search('exp*er').count(), 0)
    eq_(search('xyz').count(), 0)
