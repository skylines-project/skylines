BEGIN;

-- Table: competitions

CREATE TABLE competitions
(
  id serial NOT NULL,
  name character varying(64) NOT NULL,
  description text,
  start_date date NOT NULL,
  end_date date NOT NULL,
  time_created timestamp without time zone NOT NULL,
  time_modified timestamp without time zone NOT NULL,
  creator_id integer,
  location character varying(64),
  airport_id integer,
  CONSTRAINT competitions_pkey PRIMARY KEY (id ),
  CONSTRAINT competitions_creator_id_fkey FOREIGN KEY (creator_id)
      REFERENCES tg_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL,
  CONSTRAINT competitions_airport_id_fkey FOREIGN KEY (airport_id)
      REFERENCES airports (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL
)
WITH (
  OIDS=FALSE
);

-- Table: competition_classes

CREATE TABLE competition_classes
(
  id serial NOT NULL,
  competition_id integer NOT NULL,
  name character varying(64) NOT NULL,
  description text,
  CONSTRAINT competition_classes_pkey PRIMARY KEY (id ),
  CONSTRAINT competition_classes_competition_id_fkey FOREIGN KEY (competition_id)
      REFERENCES competitions (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);

-- Table: competition_participation

CREATE TABLE competition_participation
(
  id serial NOT NULL,
  competition_id integer NOT NULL,
  user_id integer NOT NULL,
  class_id integer,
  admin_time timestamp without time zone,
  pilot_time timestamp without time zone,
  CONSTRAINT competition_participation_pkey PRIMARY KEY (id ),
  CONSTRAINT competition_participation_competition_id_fkey FOREIGN KEY (competition_id)
      REFERENCES competitions (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT competition_participation_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES tg_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT competition_participation_class_id_fkey FOREIGN KEY (class_id)
      REFERENCES competition_classes (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL
)
WITH (
  OIDS=FALSE
);

COMMIT;
