BEGIN;

-- Add fuzzystrmatch extension for levenshtein calculations
create EXTENSION fuzzystrmatch;

COMMIT;

