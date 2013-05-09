BEGIN;

/* Create the new table */

CREATE TABLE events
(
  id serial NOT NULL,
  type integer NOT NULL,
  "time" timestamp without time zone NOT NULL,
  actor_id integer NOT NULL,
  flight_id integer,
  flight_comment_id integer,
  CONSTRAINT events_pkey PRIMARY KEY (id ),
  CONSTRAINT events_actor_id_fkey FOREIGN KEY (actor_id)
      REFERENCES tg_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT events_flight_id_fkey FOREIGN KEY (flight_id)
      REFERENCES flights (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT events_flight_comment_id_fkey FOREIGN KEY (flight_comment_id)
      REFERENCES flight_comments (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);

/* Add a new column and primary key constraint to the old notifications table */

ALTER TABLE notifications
  ADD COLUMN event_id integer;

ALTER TABLE notifications
  ADD CONSTRAINT notifications_event_id_fkey FOREIGN KEY (event_id)
      REFERENCES events (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE;

/* Copy the "new follower" notifications to the events table */

INSERT INTO events (type, time, actor_id)
SELECT type, time_created as time, sender_id as actor_id FROM notifications
WHERE type = 3;

/* .. and set the event_id column to the correct id of the events table */

UPDATE notifications
SET event_id = events.id
FROM events
WHERE notifications.time_created = events.time;

/* Copy the other notifications to the events table */

INSERT INTO events (type, time, actor_id, flight_id, flight_comment_id)
SELECT type, min(time_created) as time, sender_id as actor_id, flight_id, flight_comment_id
FROM notifications
WHERE type <> 3
GROUP BY sender_id, type, flight_id, flight_comment_id;

/* .. and set the event_id columns to the correct id of the events table */

UPDATE notifications
SET event_id = events.id
FROM events
WHERE notifications.type = 1
AND notifications.sender_id = events.actor_id
AND notifications.flight_id = events.flight_id
AND notifications.flight_comment_id = events.flight_comment_id;

UPDATE notifications
SET event_id = events.id
FROM events
WHERE notifications.type = 2
AND notifications.sender_id = events.actor_id
AND notifications.flight_id = events.flight_id;

/* Make sure there are no notifications without events */

ALTER TABLE notifications
   ALTER COLUMN event_id SET NOT NULL;

/* Drop obsolete columns */

ALTER TABLE notifications DROP COLUMN time_created;
ALTER TABLE notifications DROP COLUMN sender_id;
ALTER TABLE notifications DROP COLUMN flight_id;
ALTER TABLE notifications DROP COLUMN flight_comment_id;
ALTER TABLE notifications DROP COLUMN type;

COMMIT;
