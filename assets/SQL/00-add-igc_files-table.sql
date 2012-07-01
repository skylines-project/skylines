BEGIN;

-- Create the table that stores IGC files
CREATE TABLE igc_files
(
  id serial NOT NULL,
  owner_id integer NOT NULL,
  time_created timestamp without time zone NOT NULL,
  filename character varying NOT NULL,
  md5 character varying(32) NOT NULL,
  logger_manufacturer_id character varying(3),
  CONSTRAINT igc_files_pkey PRIMARY KEY (id ),
  CONSTRAINT igc_files_owner_id_fkey FOREIGN KEY (owner_id)
      REFERENCES tg_user (user_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT igc_files_md5_key UNIQUE (md5 )
)
WITH (
  OIDS=FALSE
);

-- Add igc_files reference column to flights table
ALTER TABLE flights ADD COLUMN igc_file_id integer;

-- Add the necessary constraint to the igc_file_id column
ALTER TABLE flights
  ADD CONSTRAINT flights_igc_file_id_fkey FOREIGN KEY (igc_file_id)
      REFERENCES igc_files (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION;

-- Copy data from flights to igc_files table
INSERT INTO igc_files (owner_id, time_created, filename,
                       md5,logger_manufacturer_id)
  SELECT owner_id, time_created, filename, md5,logger_manufacturer_id
  FROM flights;

-- Update flights.igc_file_id column
UPDATE flights
  SET igc_file_id = (SELECT id FROM igc_files
                     WHERE igc_files.md5 = flights.md5);

-- A flight should always have a igc_file_id
ALTER TABLE flights ALTER COLUMN igc_file_id SET NOT NULL;

-- Drop obsolete columns from flights table
ALTER TABLE flights DROP CONSTRAINT flights_owner_id_fkey;
ALTER TABLE flights DROP COLUMN owner_id;
ALTER TABLE flights DROP COLUMN filename;
ALTER TABLE flights DROP CONSTRAINT md5;
ALTER TABLE flights DROP COLUMN md5;
ALTER TABLE flights DROP COLUMN logger_manufacturer_id;

COMMIT;

