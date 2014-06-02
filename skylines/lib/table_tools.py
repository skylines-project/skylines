from math import ceil

from flask import request, abort, g
from sqlalchemy.sql.expression import asc, desc


class Pager:
    def __init__(self, page, count, items_per_page=20):
        self.count = count
        self.items_per_page = items_per_page

        self.page_count = int(ceil(count / float(items_per_page)))
        self.first_page = 1
        self.last_page = self.page_count

        self.page = max(min(page, self.last_page), self.first_page)

        self.offset = (self.page - 1) * items_per_page
        self.back_offset = min(self.offset + self.items_per_page, self.count)

    @classmethod
    def paginate(cls, query, name, items_per_page=20):
        count = query.count()

        try:
            page = int(request.args.get('page', 1))
        except:
            abort(400)

        pager = cls(page, count, items_per_page)

        if not hasattr(g, 'paginators'):
            g.paginators = {}

        g.paginators[name] = pager

        return query.limit(items_per_page).offset(pager.offset)

    def args(self):
        return dict(page=self.page)


class Sorter:
    def __init__(self, column, order, valid_columns):
        self.column = column
        self.order = order
        self.valid_columns = valid_columns

    @classmethod
    def sort(cls, query, name, default_column, valid_columns={}, default_order='asc'):
        try:
            column = request.args.get('column', default_column)
            order = request.args.get('order', default_order)
        except:
            abort(400)

        if column not in valid_columns:
            abort(400)

        if not hasattr(g, 'sorters'):
            g.sorters = {}

        g.sorters[name] = cls(column, order, valid_columns)

        if order == 'asc':
            return query.order_by(asc(valid_columns.get(column)))
        elif order == 'desc':
            return query.order_by(desc(valid_columns.get(column)))
        else:
            abort(400)

    def args(self):
        return dict(column=self.column,
                    order=self.order)
