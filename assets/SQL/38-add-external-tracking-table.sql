CREATE TABLE external_tracking_fixes
(
  id serial NOT NULL,
  tracking_type smallint,
  tracking_id integer NOT NULL,
  owner_id integer NOT NULL,
  ip inet,
  "time" timestamp without time zone NOT NULL,
  location geography(Point,4326),
  track smallint,
  ground_speed double precision,
  altitude smallint,
  vario double precision,
  aircraft_type smallint,
  CONSTRAINT external_tracking_fixes_pkey PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);

CREATE INDEX external_tracking_fixes_tracking_id_time
  ON external_tracking_fixes
  USING btree
  (tracking_id , "time" );


