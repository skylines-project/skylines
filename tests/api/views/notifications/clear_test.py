from skylines.model.notification import Notification, create_follower_notification

from tests.api import auth_for
from tests.data import users


def test_clear_all(db_session, client):
    john = users.john()
    jane = users.jane()
    max = users.max()

    create_follower_notification(john, jane)
    create_follower_notification(john, max)
    create_follower_notification(jane, max)

    db_session.commit()

    res = client.post("/notifications/clear", headers=auth_for(john))
    assert res.status_code == 200
    assert res.json == {}

    johns_notifications = db_session.query(Notification).filter_by(recipient=john).all()
    assert len(johns_notifications) == 2
    assert johns_notifications[0].event.actor_id == jane.id
    assert johns_notifications[0].time_read is not None
    assert johns_notifications[1].event.actor_id == max.id
    assert johns_notifications[1].time_read is not None

    janes_notifications = db_session.query(Notification).filter_by(recipient=jane).all()
    assert len(janes_notifications) == 1
    assert janes_notifications[0].event.actor_id == max.id
    assert janes_notifications[0].time_read is None


def test_clear_by_actor(db_session, client):
    john = users.john()
    jane = users.jane()
    max = users.max()

    create_follower_notification(john, jane)
    create_follower_notification(john, max)
    create_follower_notification(jane, max)

    db_session.commit()

    res = client.post(
        "/notifications/clear?user={}".format(max.id), headers=auth_for(john)
    )
    assert res.status_code == 200
    assert res.json == {}

    johns_notifications = db_session.query(Notification).filter_by(recipient=john).all()
    assert len(johns_notifications) == 2
    assert johns_notifications[0].event.actor_id == jane.id
    assert johns_notifications[0].time_read is None
    assert johns_notifications[1].event.actor_id == max.id
    assert johns_notifications[1].time_read is not None

    janes_notifications = db_session.query(Notification).filter_by(recipient=jane).all()
    assert len(janes_notifications) == 1
    assert janes_notifications[0].event.actor_id == max.id
    assert janes_notifications[0].time_read is None
