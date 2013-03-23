from sqlalchemy.sql import ColumnElement, func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm.properties import ColumnProperty


class extract_field(ColumnElement):
    def __init__(self, base, field):
        super(extract_field, self).__init__()
        self.base = base
        self.field = field


@compiles(extract_field)
def compile(expr, compiler, **kw):
    return '(' + compiler.process(expr.base) + ').' + expr.field


class cast(ColumnElement):
    def __init__(self, base, field):
        super(cast, self).__init__()
        self.base = base
        self.field = field


@compiles(cast)
def compile(expr, compiler, **kw):
    return '(' + compiler.process(expr.base) + ')::' + expr.field


class LowerCaseComparator(ColumnProperty.Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)
