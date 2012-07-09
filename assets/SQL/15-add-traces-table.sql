BEGIN;

-- Table: traces

CREATE TABLE traces
(
  id serial NOT NULL,
  flight_id integer NOT NULL,
  contest_type character varying NOT NULL,
  trace_type character varying NOT NULL,
  times timestamp without time zone[] NOT NULL,
  locations geometry NOT NULL,
  CONSTRAINT traces_pkey PRIMARY KEY (id ),
  CONSTRAINT traces_flight_id_fkey FOREIGN KEY (flight_id)
      REFERENCES flights (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT enforce_dims_locations CHECK (st_ndims(locations) = 2),
  CONSTRAINT enforce_geotype_locations CHECK (geometrytype(locations) = 'LINESTRING'::text OR locations IS NULL),
  CONSTRAINT enforce_srid_locations CHECK (st_srid(locations) = 4326)
)
WITH (
  OIDS=FALSE
);

-- Index: idx_traces_locations

CREATE INDEX idx_traces_locations
  ON traces
  USING gist
  (locations );

COMMIT;
