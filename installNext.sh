# After running this script in bash:
# to run servers:
#     Backend
#       export FLASK_ENV=development
#       pipenv run ./manage.py runserver

#     Front end in separate terminal
#       you must be skylinesC/ember
#       ember serve --proxy http://localhost:5000/
#       or
#       DEBUG=\* ember serve --proxy http://localhost:5000/

# To view website
#   http://localhost:4200/

###### Before running this script:
# run installFirst.sh

export POSTGIS_ENABLE_OUTDB_RASTERS=1
export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bionic-pgdg main" >> /etc/apt/sources.lis't
wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-10
sudo apt install -y postgresql-10-postgis-2.4
sudo apt install -y postgresql-10-postgis-scripts
sudo apt install -y postgis
sudo apt install -y postgresql-10-pgrouting

pipenv install flask
pipenv install flask_script
pipenv install flask-migrate
pipenv install geoalchemy2
pipenv install shapely
apt-get install -y libcurl4-openssl-dev libfreetype6-dev
pipenv install xcsoar
pipenv install pytz
pipenv install celery
pipenv install aerofiles
pipenv install sentry_sdk
pipenv install gevent
pipenv install crc16
pipenv install blinker
pipenv install redis
sudo apt-get install -y libpq-dev
pipenv install psycopg2
sudo apt-get install -y pkg-config

v=12
curl -sL https://deb.nodesource.com/setup_$v.x | sudo -E bash -
sudo apt-get install -y nodejs
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

sudo apt-get update && sudo apt-get install -y yarn
sudo npm install -y -g bower
sudo npm install -y -g ember-cli
cd ember
yarn install -y
bower install -y
cd ../

sudo -u postgres createuser $USER
sudo -u postgres psql -d skylines -c 'CREATE EXTENSION adminpack;'
sudo -u postgres psql -d skylines -c 'CREATE EXTENSION postgis;'
sudo -u postgres psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'

pipenv run ./manage.py db create
pipenv run ./manage.py import welt2000 --commit

