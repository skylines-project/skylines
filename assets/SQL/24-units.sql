BEGIN;
ALTER TABLE tg_user ADD COLUMN distance_unit smallint NOT NULL DEFAULT 1;
ALTER TABLE tg_user ADD COLUMN speed_unit smallint NOT NULL DEFAULT 1;
COMMIT;
