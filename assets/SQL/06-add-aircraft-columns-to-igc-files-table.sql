BEGIN;

ALTER TABLE igc_files ADD COLUMN registration character varying(32);
ALTER TABLE igc_files ADD COLUMN model character varying(64);

COMMIT;
