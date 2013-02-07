CREATE TABLE tracking_sessions
(
  id serial NOT NULL,
  pilot_id integer NOT NULL,
  lt24_id bigint,
  time_created timestamp without time zone NOT NULL,
  ip_created inet,
  time_finished timestamp without time zone,
  ip_finished inet,
  client character varying(32),
  client_version character varying(8),
  device character varying(32),
  gps_device character varying(32),
  aircraft_type smallint,
  aircraft_model character varying(64),
  finish_status smallint,
  CONSTRAINT tracking_sessions_pkey PRIMARY KEY (id ),
  CONSTRAINT "tg_user.id" FOREIGN KEY (pilot_id)
      REFERENCES tg_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE INDEX ix_tracking_sessions_lt24_id
  ON tracking_sessions
  USING btree
  (lt24_id );
