dropdb skylines_test
createdb skylines_test
psql skylines_test -c "CREATE EXTENSION postgis"
psql skylines_test -c "CREATE EXTENSION fuzzystrmatch"
psql skylines_test -f /usr/share/postgresql/9.1/contrib/postgis-2.0/legacy.sql
