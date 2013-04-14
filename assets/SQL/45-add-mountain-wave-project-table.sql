-- Table: mountain_wave_project

-- DROP TABLE mountain_wave_project;

CREATE TABLE mountain_wave_project
(
  axis_length double precision,
  main_wind_direction character varying(254),
  additional character varying(254),
  vertical double precision,
  source character varying(254),
  synoptical character varying(254),
  remark1 character varying(254),
  time_modified timestamp without time zone NOT NULL,
  name character varying,
  remark2 character varying(254),
  orientation double precision,
  id serial NOT NULL,
  rotor_height character varying(254),
  country_code character varying(2),
  weather_dir integer,
  time_created timestamp without time zone NOT NULL,
  location geometry(Point,4326),
  axis geometry(LineString,4326),
  ellipse geometry(LineString,4326),
  CONSTRAINT mountain_wave_project_pkey PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);

-- Index: idx_mountain_wave_project_axis

-- DROP INDEX idx_mountain_wave_project_axis;

CREATE INDEX idx_mountain_wave_project_axis
  ON mountain_wave_project
  USING gist
  (axis );

-- Index: idx_mountain_wave_project_ellipse

-- DROP INDEX idx_mountain_wave_project_ellipse;

CREATE INDEX idx_mountain_wave_project_ellipse
  ON mountain_wave_project
  USING gist
  (ellipse );

-- Index: idx_mountain_wave_project_location

-- DROP INDEX idx_mountain_wave_project_location;

CREATE INDEX idx_mountain_wave_project_location
  ON mountain_wave_project
  USING gist
  (location );

