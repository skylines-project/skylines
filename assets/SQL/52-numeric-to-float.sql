BEGIN;

ALTER TABLE flight_phases
   ALTER COLUMN speed TYPE real;
ALTER TABLE flight_phases
   ALTER COLUMN vario TYPE real;
ALTER TABLE flight_phases
   ALTER COLUMN glide_rate TYPE real;

COMMIT;
