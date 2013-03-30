ALTER TABLE flights ADD COLUMN locations geometry(LineString);

CREATE INDEX idx_flights_locations ON flights USING gist (locations );
