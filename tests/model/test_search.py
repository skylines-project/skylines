from skylines.model import User, Club, Airport
from skylines.model.search import combined_search_query, escape_tokens, text_to_tokens

MODELS = [User, Club, Airport]


def search(text):
    # Split the search text into tokens and escape them properly
    tokens = text_to_tokens(text)
    tokens = escape_tokens(tokens)

    # Create combined search query
    return combined_search_query(MODELS, tokens)


def test_tokenizer():
    # Check that this does not throw exceptions
    text_to_tokens(u"\\")
    text_to_tokens(u"blabla \\")
    text_to_tokens(u'"')
    text_to_tokens(u'"blabla \\')

    # Check that the tokenizer returns expected results
    assert text_to_tokens(u"a b c") == [u"a", u"b", u"c"]
    assert text_to_tokens(u"a 'b c'") == [u"a", u"b c"]
    assert text_to_tokens(u'a "b c" d') == [u"a", u"b c", u"d"]
    assert text_to_tokens(u'old "mac donald" has a FARM') == [
        u"old",
        u"mac donald",
        u"has",
        u"a",
        u"FARM",
    ]


def test_escaping():
    assert escape_tokens([u"hello!"]) == [u"hello!"]
    assert escape_tokens([u"hello *!"]) == [u"hello %!"]
    assert escape_tokens([u"hello %!"]) == [u"hello \\%!"]
    assert escape_tokens([u"hello _!"]) == [u"hello \\_!"]


def test_search(test_user, test_admin):
    assert search(u"example").count() == 2
    assert search(u"user").count() == 1
    assert search(u"man").count() == 1
    assert search(u"man*er").count() == 1
    assert search(u"*er").count() == 2
    assert search(u"exa*er").count() == 2
    assert search(u"exp*er").count() == 0
    assert search(u"xyz").count() == 0
