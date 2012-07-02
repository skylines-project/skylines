BEGIN;

ALTER TABLE tg_user ADD COLUMN login_time timestamp;

COMMIT;

