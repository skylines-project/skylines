# set environment variables

cat >> ~/.profile << EOF
export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
export POSTGIS_ENABLE_OUTDB_RASTERS=1
EOF

#remove any locks

sudo killall apt apt-get
sudo rm /var/lib/apt/lists/lock
sudo rm /var/cache/apt/archives/lock
sudo rm /var/lib/dpkg/lock*
sudo dpkg --configure -a
sudo apt update

# update apt-get repository

sudo apt-get update

# install add-apt-repository tool

sudo apt-get install -y --no-install-recommends software-properties-common

# add PPAs

sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
# sudo add-apt-repository -y ppa:jonathonf/python-2.7

# update apt-get repository

sudo apt-get update

# install base dependencies

sudo apt-get install -y --no-install-recommends \
   python python-dev \
    
sudo apt-get install -y --no-install-recommends \
    g++-6 pkg-config libcurl4-openssl-dev redis-server\
    libpq-dev libfreetype6-dev libpng-dev libffi-dev 
echo 'New libs:'
sudo apt-get install -y --no-install-recommends \
    ibgeos-c1 liblwgeom-2.2-5

sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bionic-pgdg main" >> /etc/apt/sources.lis't
wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-10
sudo apt install -y postgresql-10-postgis-2.4
sudo apt install -y postgresql-10-postgis-scripts
sudo apt install -y postgis
sudo apt install -y postgresql-10-pgrouting

# set GCC 6 as default

sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 60 --slave /usr/bin/g++ g++ /usr/bin/g++-6

# install pip

wget -N -nv https://bootstrap.pypa.io/get-pip.py
sudo -H python get-pip.py
   
# install pipenv

sudo -H pip install pipenv
sudo apt-get install -y pkg-config

# install skylines and the python dependencies
apt-get install -y libcurl4-openssl-dev libfreetype6-dev
sudo apt-get install -y libpq-dev
pipenv install --verbose --skip-lock flask
pipenv install --verbose --skip-lock babel
pipenv install --verbose --skip-lock flask-caching
pipenv install --verbose --skip-lock flask-migrate
pipenv install --verbose --skip-lock flask_script
pipenv install --verbose --skip-lock flask-sqlalchemy
pipenv install --verbose --skip-lock psycopg2
pipenv install --verbose --skip-lock geoalchemy2
pipenv install --verbose --skip-lock shapely
pipenv install --verbose --skip-lock crc16
pipenv install --verbose --skip-lock pytz
pipenv install --verbose --skip-lock celery
pipenv install --verbose --skip-lock redis
pipenv install --verbose --skip-lock xcsoar
pipenv install --verbose --skip-lock aerofiles
pipenv install --verbose --skip-lock enum34
pipenv install --verbose --skip-lock pyproj
pipenv install --verbose --skip-lock gevent
pipenv install --verbose --skip-lock webargs
pipenv install --verbose --skip-lock flask-oauthlib
pipenv install --verbose --skip-lock requests-oauthlib
pipenv install --verbose --skip-lock sentry-sdk
pipenv install --verbose --skip-lock mapproxy
pipenv install --verbose --skip-lock sentry_sdk
pipenv install --verbose --skip-lock gunicorn
pipenv install --verbose --skip-lock fabric
pipenv install --verbose --skip-lock pytest
pipenv install --verbose --skip-lock pytest-cov
pipenv install --verbose --skip-lock pytest-voluptuous
pipenv install --verbose --skip-lock mock
pipenv install --verbose --skip-lock faker
pipenv install --verbose --skip-lock flake8
pipenv install --verbose --skip-lock immobilus
pipenv install --verbose --skip-lock blinker


# pipenv install --verbose --dev  --skip-lock #this doesn't work with skip-lock...seems to work without it, but can't lock anyway due to oauth dependency problems

# create PostGIS databases

sudo sudo -u postgres createuser -s $USER

sudo sudo -u postgres createdb skylines -O $USER
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'

sudo sudo -u postgres createdb skylines_test -O $USER
sudo sudo -u postgres psql -d skylines_test -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines_test -c 'CREATE EXTENSION fuzzystrmatch;'

sudo sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'secret123';"

pipenv run ./manage.py db create

# create folder for downloaded files
mkdir -p htdocs/files
mkdir -p htdocs/srtm

# Front end
#add-apt-repository may not be present on some Ubuntu releases:
sudo apt-get install python-software-properties

sudo add-apt-repository -y -r ppa:chris-lea/node.js
sudo rm -f /etc/apt/sources.list.d/chris-lea-node_js-*.list
sudo rm -f /etc/apt/sources.list.d/chris-lea-node_js-*.list.save
curl -sSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo apt-key add -
VERSION=node_12.x
DISTRO="$(lsb_release -s -c)"
echo "deb https://deb.nodesource.com/$VERSION $DISTRO main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get update
sudo apt-get install -y nodejs

curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
echo "deb-src https://deb.nodesource.com/$VERSION $DISTRO main" | sudo tee -a /etc/apt/sources.list.d/nodesource.list

sudo apt-get update && sudo apt-get install -y yarn
sudo npm install -y -g bower
sudo npm install -y -g ember-cli

cd ember
yarn install
sudo bower install --allow-root
cd ../
sudo chown $USER -R ~/.config/*

# management
npm install pm2
#pipenv run ./manage.py import welt2000 --commit

# production server
#sudo ufw enable
