BEGIN;

-- Add airport name column to flights table
ALTER TABLE flights ADD COLUMN takeoff_airport_id integer;

-- Add relation to airports table
ALTER TABLE flights
  ADD CONSTRAINT flights_takeoff_airport_id_fkey FOREIGN KEY (takeoff_airport_id)
      REFERENCES airports (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION;

COMMIT;

