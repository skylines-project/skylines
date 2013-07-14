BEGIN;

/* Add a new column and primary key constraint to the events table */

ALTER TABLE events
  ADD COLUMN user_id integer;

ALTER TABLE events
  ADD CONSTRAINT events_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES tg_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE;

UPDATE events
  SET user_id = notifications.recipient_id
  FROM notifications
  WHERE notifications.event_id = events.id
    AND events.type = 3;

COMMIT;
