from sqlalchemy.sql import ColumnElement, func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.types import to_instance


class PGCompositeElement(ColumnElement):
    def __init__(self, base, field, type_):
        ColumnElement.__init__(self)
        self.base = base
        self.field = field
        self.type = to_instance(type_)


@compiles(PGCompositeElement)
def _compile_pgelem(expr, compiler, **kw):
    return '(%s).%s' % (compiler.process(expr.base, **kw), expr.field)


class LowerCaseComparator(ColumnProperty.Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)
