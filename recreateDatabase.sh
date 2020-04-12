sudo sudo -u postgres createdb skylines -O $USER
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'
#pipenv run ./manage.py db create
#pg_restore -d skylines  --data-only  -t airports -t models /home/bret/servers/database_backups/airportsModels.custom
