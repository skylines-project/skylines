BEGIN;
ALTER TABLE tg_user RENAME COLUMN user_id TO id;
ALTER TABLE tg_group RENAME COLUMN group_id TO id;
ALTER TABLE tg_permission RENAME COLUMN permission_id TO id;
COMMIT;
