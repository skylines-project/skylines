BEGIN;

ALTER TABLE notifications ADD COLUMN type integer;
UPDATE notifications SET type = 1;
ALTER TABLE notifications ALTER COLUMN type SET NOT NULL;

COMMIT;
