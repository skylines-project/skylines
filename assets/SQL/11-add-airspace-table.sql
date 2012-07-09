BEGIN;

-- Table: airspace

-- DROP TABLE airspace;

CREATE TABLE airspace
(
  id serial NOT NULL,
  time_created timestamp without time zone NOT NULL,
  time_modified timestamp without time zone NOT NULL,
  name character varying NOT NULL,
  airspace_class character varying(3) NOT NULL,
  base character varying(30) NOT NULL,
  top character varying(30) NOT NULL,
  country_code character varying(2) NOT NULL,
  the_geom geometry,
  CONSTRAINT airspace_pkey PRIMARY KEY (id ),
  CONSTRAINT enforce_dims_the_geom CHECK (st_ndims(the_geom) = 2),
  CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(the_geom) = 'POLYGON'::text OR the_geom IS NULL),
  CONSTRAINT enforce_srid_the_geom CHECK (st_srid(the_geom) = 4326)
)
WITH (
  OIDS=FALSE
);

-- Index: idx_airspace_the_geom

-- DROP INDEX idx_airspace_the_geom;

CREATE INDEX idx_airspace_the_geom
  ON airspace
  USING gist
  (the_geom );

-- register geometry column
INSERT INTO geometry_columns(f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, "type")
SELECT '', 'public', 'airspace', 'the_geom', 2, 4326, 'POLYGON';


COMMIT;
