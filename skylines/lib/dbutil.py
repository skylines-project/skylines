# -*- coding: utf-8 -*-

"""Database helpers used in SkyLines."""

from sqlalchemy import orm
from webob.exc import HTTPNotFound
from skylines.model import DBSession


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
        raise HTTPNotFound

    q = DBSession.query(model)
    q = _patch_query(q, **kw)
    record = q.get(id)
    if record is None:
        raise HTTPNotFound
    return record


def _parse_id_list(ids):
    out = list()
    for id in ids.split(','):
        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound
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
    result = list(q)
    if len(result) != len(ids):
        raise HTTPNotFound

    return result
