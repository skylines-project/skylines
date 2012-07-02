BEGIN;

-- Table: airports

CREATE TABLE airports
(
  id serial NOT NULL,
  time_created timestamp without time zone NOT NULL,
  time_modified timestamp without time zone NOT NULL,
  altitude double precision,
  name character varying NOT NULL,
  short_name character varying,
  icao character varying(4),
  country_code character varying(2) NOT NULL,
  surface character varying(10),
  runway_len integer,
  runway_dir integer,
  frequency double precision,
  type character varying(20),
  location_wkt geometry,
  CONSTRAINT airports_pkey PRIMARY KEY (id ),
  CONSTRAINT enforce_dims_location_wkt CHECK (st_ndims(location_wkt) = 2),
  CONSTRAINT enforce_geotype_location_wkt CHECK (geometrytype(location_wkt) = 'POINT'::text OR location_wkt IS NULL),
  CONSTRAINT enforce_srid_location_wkt CHECK (st_srid(location_wkt) = 4326)
)
WITH (
  OIDS=FALSE
);

CREATE INDEX idx_airports_location_wkt
  ON airports
  USING gist
  (location_wkt );

COMMIT;

