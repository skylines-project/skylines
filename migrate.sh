### migrate database when changing schema ##
DATE_TIME=`date "+%Y%m%d-%H%M%S"` #add %3N as we want millisecond too
echo 'Migrating skylines database, $DATE_TIME'
sudo -u bret pg_dump skylines > dbdump$DATE_TIME.sql

#destroy database
sudo dropdb skylines

#recreate
sudo sudo -u postgres createdb skylines -O $USER
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'
sudo -u bret pipenv run ./manage.py db create

#restore date
sudo -u bret psql -d skylines -f dbdump$DATE_TIME.sql
