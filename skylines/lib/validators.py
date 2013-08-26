from flask.ext.babel import _

from formencode.api import FancyValidator, Invalid
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, not_
from werkzeug.datastructures import FileStorage


class UniqueValueUnless(FancyValidator):
    def __init__(self, filter_func, session, entity, field_name, *args, **kw):
        self.filter_func = filter_func
        self.session = session
        self.entity = entity
        self.field_name = field_name
        FancyValidator.__init__(self, *args, **kw)

    def _is_unique_unless(self, entity, field_name, value):
        field = getattr(entity, field_name)
        filter = (field == value)

        if self.filter_func is not None:
            additional_filter = self.filter_func(entity)
            if additional_filter is not None:
                filter = and_(filter, not_(additional_filter))

        try:
            self.session.query(entity).filter(filter).one()
        except NoResultFound:
            return True
        return False

    def _to_python(self, value, state):
        if not self._is_unique_unless(self.entity, self.field_name, value):
            raise Invalid(_('That value already exists'), value, state)
        return value


class FileFieldValidator(FancyValidator):
    """
    Handles werkzeug.datastructures.FileStorage instances.

    This doesn't do any conversion, but it can detect empty upload
    fields (which appear like normal fields, but have no filename when
    no upload was given).
    """
    def _convert_to_python(self, value, state=None):
        if isinstance(value, FileStorage):
            if getattr(value, 'filename', None):
                return value
            raise Invalid('invalid', value, state)
        else:
            return value

    def is_empty(self, value):
        if isinstance(value, FileStorage):
            return not bool(getattr(value, 'filename', None))
        return FancyValidator.is_empty(self, value)
