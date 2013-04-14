CREATE TABLE elevations
(
  rid serial NOT NULL,
  rast raster,
  CONSTRAINT elevations_pkey PRIMARY KEY (rid )
)
WITH (
  OIDS=FALSE
);

CREATE INDEX elevations_rast_gist
  ON elevations
  USING gist
  (st_convexhull(rast) );
