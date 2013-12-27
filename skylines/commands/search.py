from flask.ext.script import Command, Option

from skylines.model import User, Club, Airport
from skylines.model.search import combined_search_query, escape_tokens

MODELS = [User, Club, Airport]


class Search(Command):

    option_list = (
        Option('tokens', metavar='TOKEN', nargs='*',
               help='Any number of tokens to search for'),
    )

    def run(self, tokens):
        for u in self.search_query(tokens).limit(20):
            model = globals()[u.model]
            instance = model.get(u.id)

            print u.weight, instance, u.details

    def search_query(self, tokens):
        tokens = escape_tokens(tokens)
        return combined_search_query(MODELS, tokens)
