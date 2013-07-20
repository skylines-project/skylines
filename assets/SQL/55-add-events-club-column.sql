BEGIN;

/* Add a new column and primary key constraint to the events table */

ALTER TABLE events
  ADD COLUMN club_id integer;

ALTER TABLE events
  ADD CONSTRAINT events_club_id_fkey FOREIGN KEY (club_id)
      REFERENCES clubs (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE;

COMMIT;
