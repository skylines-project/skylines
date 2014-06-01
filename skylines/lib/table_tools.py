from math import ceil

from flask import request, abort, g


class Pager:
    def __init__(self, page, count, items_per_page=20):
        self.count = count
        self.items_per_page = items_per_page

        self.page_count = int(ceil(count / float(items_per_page)))
        self.first_page = 1
        self.last_page = self.page_count - 1

        self.page = max(min(page, self.last_page), self.first_page)

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

        offset = (pager.page - 1) * items_per_page
        return query.limit(items_per_page).offset(offset)
