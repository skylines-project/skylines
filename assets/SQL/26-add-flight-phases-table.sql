CREATE TABLE flight_phases
(
  id serial NOT NULL,
  flight_id integer NOT NULL,
  start_time timestamp without time zone,
  end_time timestamp without time zone,
  aggregate boolean NOT NULL,
  circling_direction integer,
  phase_type integer,
  alt_diff integer,
  duration interval,
  fraction integer,
  distance integer,
  speed numeric(9,2),
  vario numeric(9,2),
  glide_rate numeric(9,2),
  count integer NOT NULL,
  CONSTRAINT flight_phases_pkey PRIMARY KEY (id ),
  CONSTRAINT flight_phases_flight_id_fkey FOREIGN KEY (flight_id)
      REFERENCES flights (id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);

CREATE INDEX flight_phases_flight_id_idx
  ON flight_phases
  USING btree
  (flight_id );

