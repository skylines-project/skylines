#!/usr/bin/env bash

raster2pgsql -a -e -s 4326 -t 100x100 unzipped/*.hgt elevations | psql
