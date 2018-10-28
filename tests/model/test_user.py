# -*- coding: utf-8 -*-

import os
import pytest

from skylines.lib import files
from skylines.lib.types import is_unicode
from skylines.model import User, IGCFile
from tests.data import users, igcs


def test_user_delete_deletes_user(db_session):
    john = users.john()
    db_session.add(john)
    db_session.commit()

    john_id = john.id
    assert john_id is not None

    assert db_session.query(User).get(john_id) is not None

    john.delete()
    db_session.commit()

    assert db_session.query(User).get(john_id) is None


@pytest.mark.usefixtures("files_folder")
def test_user_delete_deletes_owned_igc_files(db_session):
    with open(igcs.simple_path, "rb") as f:
        filename = files.add_file("simple.igc", f)

    assert filename is not None
    assert os.path.isfile(files.filename_to_path(filename))

    john = users.john()
    igc = igcs.simple(owner=john, filename=filename)
    db_session.add(igc)
    db_session.commit()

    assert db_session.query(IGCFile).count() == 1
    assert db_session.query(IGCFile).get(igc.id).owner_id == john.id

    john.delete()
    db_session.commit()

    assert db_session.query(IGCFile).count() == 0
    assert not os.path.isfile(files.filename_to_path(filename))


def test_repr_is_str(db_session):
    john = users.john(last_name=u"Müller")
    db_session.add(john)
    db_session.commit()

    assert isinstance(repr(john), str)
    assert repr(john) == "<User: email=johnny@doe.com, display=John Müller>"


def test_hash_password():
    hash = User._hash_password(u"secret123", salt=b"abcdef")
    assert (
        hash
        == "bef57ec7f53a6d40beb640a780a639c83bc29ac8a9816f1fc6c5c6dcd93c4721272b82aa344691fb4037f20617b1d19212042e7e6cb39f4ba0dad95d8137104a"
    )
    assert is_unicode(hash)
