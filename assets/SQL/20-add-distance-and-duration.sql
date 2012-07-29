BEGIN;
ALTER TABLE traces ADD COLUMN distance integer;
ALTER TABLE traces ADD COLUMN duration interval;
COMMIT;
