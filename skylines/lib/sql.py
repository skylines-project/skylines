from sqlalchemy.sql import ColumnElement
from sqlalchemy.ext.compiler import compiles


class extract_field(ColumnElement):
    def __init__(self, base, field):
        self.base = base
        self.field = field
        # throws an error unless declared...
        self.type = None


@compiles(extract_field)
def compile(expr, compiler, **kw):
    return '(' + compiler.process(expr.base) + ').' + expr.field
