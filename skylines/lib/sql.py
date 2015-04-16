from sqlalchemy.sql import func, ColumnElement, literal_column, cast, and_
from sqlalchemy.types import String, Integer
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm.properties import ColumnProperty
from geoalchemy2.functions import GenericFunction


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
    return cast(and_(self != None, self.ilike(value)), Integer) * weight

# Inject weighted_ilike() method into String type
setattr(String.comparator_factory, 'weighted_ilike', weighted_ilike)


class _ST_Intersects(GenericFunction):
    """
    ST_Intersects without index search
    """
    name = '_ST_Intersects'
    type = None


class _ST_Contains(GenericFunction):
    """
    ST_Contains without index search
    """
    name = '_ST_Contains'
    type = None


def query_to_sql(query):
    """
    Convert a sqlalchemy query to raw SQL.
    https://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression
    """

    from psycopg2.extensions import adapt as sqlescape

    statement = query.statement.compile(dialect=query.session.bind.dialect)
    dialect = query.session.bind.dialect

    enc = dialect.encoding
    params = {}

    for k, v in statement.params.iteritems():
        if isinstance(v, unicode):
            v = v.encode(enc)
        params[k] = sqlescape(v)

    return (statement.string.encode(enc) % params).decode(enc)
