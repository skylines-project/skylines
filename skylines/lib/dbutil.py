# -*- coding: utf-8 -*-

"""Database helpers used in SkyLines."""

from werkzeug.exceptions import NotFound
from flask.ext.babel import _
from sqlalchemy import orm


def _patch_query(q, joinedload=(), patch_query=None):
    if joinedload:
        q = q.options(orm.joinedload(*joinedload))

    if patch_query:
        q = patch_query(q)

    return q


def get_requested_record(model, id, **kw):
    """Look up a record with the id (string) specified by a remote
    client.  Aborts the current request if the id is malformed or if
    the record does not exist."""

    try:
        id = int(id)
    except ValueError:
        raise NotFound(description=_('Sorry, the record id ({id}) that you '
                                     'requested is not a valid id.').format(id=id))

    q = _patch_query(model.query(), **kw)
    record = q.get(id)
    if record is None:
        raise NotFound(description=_('Sorry, there is no such record ({id}) in '
                                     'our database.').format(id=id))

    return record


def _parse_id_list(ids):
    out = list()
    for id in ids.split(','):
        try:
            id = int(id)
        except ValueError:
            raise NotFound(description=_('Sorry, the record id ({id}) that you '
                                         'requested is not a valid id.').format(id=id))
        if id not in out:
            out.append(id)
    return out


def get_requested_record_list(model, ids, **kw):
    """Similar to get_requested_record(), but expects a
    comma-separated list of ids, and returns a list of (unique)
    records."""

    ids = _parse_id_list(ids)
    q = model.query().filter(model.id.in_(ids))
    q = _patch_query(q, **kw)
    records = {record.id: record for record in q}
    if len(records) != len(ids):
        raise NotFound(
            description=_('Sorry, {num_missing} of the requested records ({ids}) do not exist in our database.')
            .format(num_missing=(len(ids) - len(records)), ids=ids))

    return [records[id] for id in ids]
