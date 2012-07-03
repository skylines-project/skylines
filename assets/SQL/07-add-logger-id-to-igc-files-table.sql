BEGIN;

ALTER TABLE igc_files ADD COLUMN logger_id character varying(3);

COMMIT;
