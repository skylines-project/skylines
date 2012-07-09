BEGIN;

-- Add a unique lower case email_address index
CREATE UNIQUE INDEX users_lower_email_address_idx ON tg_user(lower(email_address));

COMMIT;

