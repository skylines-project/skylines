BEGIN;

ALTER TABLE flights ADD COLUMN date_local date;
UPDATE flights SET date_local = takeoff_time;
ALTER TABLE flights ALTER COLUMN date_local SET NOT NULL;

CREATE INDEX ix_flights_date_local
  ON flights
  USING btree
  (date_local );

COMMIT;
