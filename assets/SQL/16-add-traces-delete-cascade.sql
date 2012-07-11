BEGIN;

-- add delete cascade to traces table
-- note: a constraint can't be altered, so it must be dropped and added

ALTER TABLE traces DROP CONSTRAINT traces_flight_id_fkey;

ALTER TABLE traces ADD CONSTRAINT traces_flight_id_fkey FOREIGN KEY (flight_id)
  REFERENCES flights(id) MATCH SIMPLE
  ON UPDATE NO ACTION ON DELETE CASCADE;

COMMIT;

