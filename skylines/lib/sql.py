from sqlalchemy.sql import ColumnElement, func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.types import UserDefinedType, to_instance


class PGCompositeElement(ColumnElement):
    def __init__(self, base, field, type_):
        ColumnElement.__init__(self)
        self.base = base
        self.field = field
        self.type = to_instance(type_)


@compiles(PGCompositeElement)
def _compile_pgelem(expr, compiler, **kw):
    return '(%s).%s' % (compiler.process(expr.base, **kw), expr.field)


class PGCompositeType(UserDefinedType):
    def __init__(self, typemap):
        self.typemap = typemap

    class comparator_factory(UserDefinedType.Comparator):
        def __getattr__(self, key):
            try:
                type_ = self.type.typemap[key]
            except KeyError:
                raise KeyError("Type '%s' doesn't have an attribute: '%s'" % (self.type, key))

            return PGCompositeElement(self.expr, key, type_)


class LowerCaseComparator(ColumnProperty.Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)
