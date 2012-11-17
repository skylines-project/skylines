# -*- coding: utf-8 -*-

"""Database helpers used in SkyLines."""

from tg.i18n import ugettext as _
from sqlalchemy import orm
from webob.exc import HTTPNotFound
from skylines.model.session import DBSession


def _patch_query(q, joinedload=()):
    if joinedload:
        q = q.options(orm.joinedload(*joinedload))
    return q


def get_requested_record(model, id, **kw):
    """Look up a record with the id (string) specified by a remote
    client.  Aborts the current request if the id is malformed or if
    the record does not exist."""

    try:
        id = int(id)
    except ValueError:
        raise HTTPNotFound(detail=_('Sorry, the record id ({id}) that you ' \
                                    'requested is not a valid id.').format(id=id))

    q = DBSession.query(model)
    q = _patch_query(q, **kw)
    record = q.get(id)
    if record is None:
        raise HTTPNotFound(detail=_('Sorry, there is no such record ({id}) in ' \
                                    'our database.').format(id=id))

    return record


def _parse_id_list(ids):
    out = list()
    for id in ids.split(','):
        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound(detail=_('Sorry, the record id ({id}) that you ' \
                                        'requested is not a valid id.').format(id=id))
        if id not in out:
            out.append(id)
    return out


def get_requested_record_list(model, ids, **kw):
    """Similar to get_requested_record(), but expects a
    comma-separated list of ids, and returns a list of (unique)
    records."""

    ids = _parse_id_list(ids)
    q = DBSession.query(model).filter(model.id.in_(ids))
    q = _patch_query(q, **kw)
    records = {record.id: record for record in q}
    if len(records) != len(ids):
        raise HTTPNotFound(detail=_('Sorry, {num_missing} of the requested records ({ids}) do not exist in our database.') \
                                    .format(num_missing=(len(ids) - len(records)),
                                            ids=ids))

    return [records[id] for id in ids]
