BEGIN;

UPDATE tg_user SET display_name = user_name WHERE display_name IS NULL;
ALTER TABLE tg_user ALTER COLUMN display_name SET NOT NULL;

COMMIT;
