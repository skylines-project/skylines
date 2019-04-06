$script = <<SCRIPT

set -e

# set environment variables

cat >> ~/.profile << EOF
export LANG=C
export LC_CTYPE=C

export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
export POSTGIS_ENABLE_OUTDB_RASTERS=1
EOF

# update apt-get repository

sudo apt-get update

# install add-apt-repository tool

sudo apt-get install -y --no-install-recommends python-software-properties

# add PPAs

sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo add-apt-repository -y ppa:jonathonf/python-2.7

sudo add-apt-repository -y "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main"
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# update apt-get repository

sudo apt-get update

# install base dependencies

sudo apt-get install -y --no-install-recommends \
    python python-dev \
    g++-6 pkg-config libcurl4-openssl-dev git redis-server \
    libpq-dev postgresql-9.5-postgis-2.2 postgresql-9.5-postgis-2.2-scripts postgresql-contrib-9.5 \
    libfreetype6-dev libpng-dev libffi-dev

# set GCC 6 as default

sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 60 --slave /usr/bin/g++ g++ /usr/bin/g++-6

# install pip

wget -N -nv https://bootstrap.pypa.io/get-pip.py
sudo -H python get-pip.py

# install pipenv

sudo -H pip install pipenv

# install skylines and the python dependencies

cd /vagrant
pipenv install --dev

# create PostGIS databases

sudo sudo -u postgres createuser -s vagrant

sudo sudo -u postgres createdb skylines -O vagrant
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'

sudo sudo -u postgres createdb skylines_test -O vagrant
sudo sudo -u postgres psql -d skylines_test -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines_test -c 'CREATE EXTENSION fuzzystrmatch;'

sudo sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'secret123';"

pipenv run ./manage.py db create

# create folder for downloaded files

mkdir -p /vagrant/htdocs/files
mkdir -p /vagrant/htdocs/srtm


SCRIPT

Vagrant.configure("2") do |config|
  # TravisCI uses a Trusty Tahr base image (2018-05-26)
  config.vm.box = 'ubuntu/trusty64'

  # increase memory size, required by 'npm install'
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end

  config.vm.network 'forwarded_port', guest: 5000, host: 5000
  config.vm.network 'forwarded_port', guest: 5001, host: 5001
  config.vm.network 'forwarded_port', guest: 5597, host: 5597, protocol: 'udp'

  config.vm.provision 'shell', inline: $script, privileged: false
end
