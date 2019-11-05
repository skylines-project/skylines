# After running this script in bash:
# to run servers:
#     Backend
#       export FLASK_ENV=development
#       pipenv run ./manage.py runserver

#     Front end in separate terminal
#       you must be skylinesC/ember
#       ember serve --proxy http://localhost:5000/
#       or
#       DEBUG=\* ember serve  --proxy http://localhost:5000/

# To view website
#   http://localhost:4200/


#port forwarding needed between host and guest, from vagrant file
  # config.vm.network 'forwarded_port', guest: 5000, host: 5000
  # config.vm.network 'forwarded_port', guest: 5001, host: 5001
  # config.vm.network 'forwarded_port', guest: 5597, host: 5597, protocol: 'udp'

  # config.vm.provision 'shell', inline: $script, privileged: false


sudo apt install -y git
sudo apt install -y curl
#git clone https://github.com/hess8/skylinesC
cd skylinesC

# set environment variables

cat >> ~/.profile << EOF
export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
export POSTGIS_ENABLE_OUTDB_RASTERS=1
EOF

# update apt-get repository

sudo apt-get update

# install add-apt-repository tool

sudo apt-get install -y --no-install-recommends software-properties-common

# add PPAs

sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo add-apt-repository -y ppa:jonathonf/python-2.7

# update apt-get repository
c

sudo apt-get update

# install base dependencies

sudo apt-get install -y --no-install-recommends \
    python python-dev \
    
sudo apt-get install -y --no-install-recommends \
    g++-6 pkg-config libcurl4-openssl-dev redis-server\
    libpq-dev libfreetype6-dev libpng-dev libffi-dev 
echo 'New libs:'
sudo apt-get install -y --no-install-recommends \
    libgdal1h ibgeos-c1 libjson-c2 liblwgeom-2.2-5 libproj0

 #    The following packages have unmet dependencies:
 # postgresql-9.5-postgis-2.2 : Depends: libgdal1h (>= 1.9.0) but it is not installable
 #                              Depends: libgeos-c1 (>= 3.4.2) but it is not installable
 #                              Depends: libjson-c2 (>= 0.11) but it is not installable
 #                              Depends: liblwgeom-2.2-5 (>= 2.2.0) but it is not going to be installed
 #                              Depends: libproj0 (>= 4.8.0-1) but it is not installable


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



# install skylines and the python dependencies

pipenv install --dev

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
v=12
curl -sL https://deb.nodesource.com/setup_$v.x | sudo -E bash -
sudo apt-get install -y nodejs

curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

sudo apt-get update && sudo apt-get install -y yarn
sudo npm install -y -g bower
sudo npm install -y -g ember-cli

cd ember
yarn install
bower install
cd ../

# save for last
pipenv run ./manage.py import welt2000 --commit
