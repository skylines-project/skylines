BEGIN;

ALTER TABLE tracking_fixes ADD COLUMN ip inet;
ALTER TABLE tg_user ADD COLUMN created_ip inet;
ALTER TABLE tg_user ADD COLUMN login_ip inet;

COMMIT;

