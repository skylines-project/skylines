BEGIN;
ALTER TABLE tracking_fixes RENAME COLUMN location_wkt TO location;
ALTER TABLE flights RENAME COLUMN takeoff_location_wkt TO takeoff_location;
ALTER TABLE flights RENAME COLUMN landing_location_wkt TO landing_location;
COMMIT;
