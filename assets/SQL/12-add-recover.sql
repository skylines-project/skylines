BEGIN;

ALTER TABLE tg_user ADD COLUMN recover_key int;
ALTER TABLE tg_user ADD COLUMN recover_time timestamp;
ALTER TABLE tg_user ADD COLUMN recover_ip inet;

COMMIT;

