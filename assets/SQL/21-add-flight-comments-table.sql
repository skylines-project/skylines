BEGIN;
CREATE TABLE flight_comments
(
  id serial NOT NULL,
  time_created timestamp without time zone NOT NULL,
  flight_id integer NOT NULL,
  user_id integer,
  text character varying NOT NULL,
  CONSTRAINT flight_comments_pkey PRIMARY KEY (id ),
  CONSTRAINT flight_comments_flight_id_fkey FOREIGN KEY (flight_id)
      REFERENCES flights (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT flight_comments_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES tg_user (user_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL
)
WITH (
  OIDS=FALSE
);
COMMIT;
