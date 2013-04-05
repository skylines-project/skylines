from sqlalchemy.sql import func
from sqlalchemy.orm.properties import ColumnProperty


class LowerCaseComparator(ColumnProperty.Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)
