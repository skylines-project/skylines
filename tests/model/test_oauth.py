from skylines.model import User, RefreshToken
from tests.data import users


def test_refresh_token_is_deleted_when_user_is_deleted(db_session):
    john = users.john()
    token = RefreshToken(refresh_token="secret123", user=john)
    db_session.add(token)
    db_session.commit()

    john_id = john.id

    assert db_session.query(User).filter_by(id=john_id).count() == 1
    assert db_session.query(RefreshToken).filter_by(user_id=john_id).count() == 1

    db_session.delete(john)

    assert db_session.query(User).filter_by(id=john_id).count() == 0
    assert db_session.query(RefreshToken).filter_by(user_id=john_id).count() == 0
