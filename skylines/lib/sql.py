from sqlalchemy.sql import func, ColumnElement
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
