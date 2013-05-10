from sqlalchemy.sql import func, ColumnElement, literal_column, cast
from sqlalchemy.types import String, Integer
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm.properties import ColumnProperty


class LowerCaseComparator(ColumnProperty.Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)


class extract_array_item(ColumnElement):
    def __init__(self, array, index):
        self.array = array
        self.index = index
        # throws an error unless declared...
        self.type = None


@compiles(extract_array_item)
def compile(expr, compiler, **kw):
    return compiler.process(expr.array) + '[' + str(expr.index) + ']'


def weighted_ilike(self, value, weight=1):
    """ Calls the ILIKE operator and returns either 0 or the given weight. """

    # Make sure weight is numeric and we can safely
    # pass it to the literal_column()
    assert isinstance(weight, (int, float))

    # Convert weight to a literal_column()
    weight = literal_column(str(weight))

    # Return ilike expression
    return cast(self.ilike(value), Integer) * weight

# Inject weighted_ilike() method into String type
setattr(String.comparator_factory, 'weighted_ilike', weighted_ilike)
