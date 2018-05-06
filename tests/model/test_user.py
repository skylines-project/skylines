from skylines.model import User
from tests.data import users


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
