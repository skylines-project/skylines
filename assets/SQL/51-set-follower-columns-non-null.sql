BEGIN;

DELETE FROM followers WHERE source_id IS NULL;
DELETE FROM followers WHERE destination_id IS NULL;

ALTER TABLE followers
   ALTER COLUMN source_id SET NOT NULL;

ALTER TABLE followers
   ALTER COLUMN destination_id SET NOT NULL;

COMMIT;
