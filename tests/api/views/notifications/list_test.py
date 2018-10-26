from pytest_voluptuous import S
from voluptuous.validators import ExactSequence, Datetime

from skylines.model.notification import create_follower_notification

from tests.api import auth_for
from tests.data import users


def test_list_all(db_session, client):
    john = users.john()
    jane = users.jane()
    max = users.max()

    create_follower_notification(john, jane)
    create_follower_notification(john, max)
    create_follower_notification(jane, max)

    db_session.commit()

    res = client.get("/notifications", headers=auth_for(john))
    assert res.status_code == 200
    assert res.json == S(
        {
            u"events": ExactSequence(
                [
                    {
                        u"actor": {u"id": int, u"name": u"Max Mustermann"},
                        u"id": int,
                        u"time": Datetime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
                        u"type": u"follower",
                        u"unread": True,
                        u"user": {u"id": int, u"name": u"John Doe"},
                    },
                    {
                        u"actor": {u"id": int, u"name": u"Jane Doe"},
                        u"id": int,
                        u"time": Datetime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
                        u"type": u"follower",
                        u"unread": True,
                        u"user": {u"id": int, u"name": u"John Doe"},
                    },
                ]
            )
        }
    )
