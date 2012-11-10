dropdb skylines
createdb skylines
psql skylines -c "CREATE EXTENSION postgis"
psql skylines -c "CREATE EXTENSION fuzzystrmatch"
psql skylines -f /usr/share/postgresql/9.1/contrib/postgis-2.0/legacy.sql
