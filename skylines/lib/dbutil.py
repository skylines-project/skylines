# -*- coding: utf-8 -*-

"""Database helpers used in SkyLines."""

from webob.exc import HTTPNotFound
from skylines.model import DBSession


def get_requested_record(model, id):
    """Look up a record with the id (string) specified by a remote
    client.  Aborts the current request if the id is malformed or if
    the record does not exist."""

    try:
        id = int(id)
    except ValueError:
        raise HTTPNotFound

    record = DBSession.query(model).get(id)
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


def get_requested_record_list(model, ids):
    """Similar to get_requested_record(), but expects a
    comma-separated list of ids, and returns a list of (unique)
    records."""

    ids = _parse_id_list(ids)
    q = DBSession.query(model).filter(model.id.in_(ids))
    result = list(q)
    if len(result) != len(ids):
        raise HTTPNotFound

    return result
