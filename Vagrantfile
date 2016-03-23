$script = <<SCRIPT

# set environment variables

cat >> ~/.profile << EOF
export LANG=C
export LC_CTYPE=C

export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
export POSTGIS_ENABLE_OUTDB_RASTERS=1
EOF

# adjust apt-get repository URLs

sudo bash -c "cat > /etc/apt/sources.list" << EOF
deb mirror://mirrors.ubuntu.com/mirrors.txt precise main restricted universe multiverse
deb mirror://mirrors.ubuntu.com/mirrors.txt precise-updates main restricted universe multiverse
deb mirror://mirrors.ubuntu.com/mirrors.txt precise-backports main restricted universe multiverse
deb mirror://mirrors.ubuntu.com/mirrors.txt precise-security main restricted universe multiverse
EOF

sudo bash -c "cat > /etc/apt/sources.list.d/pgdg.list" << EOF
deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main
EOF

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# update apt-get repository

sudo apt-get update

# install base dependencies

sudo apt-get install -y --no-install-recommends \
    g++ pkg-config libcurl4-openssl-dev python-dev git \
    libpq-dev postgresql-9.4-postgis-2.2 postgresql-contrib-9.4 \
    openjdk-7-jre-headless libfreetype6-dev libpng-dev

# install pip

wget -N -nv https://bootstrap.pypa.io/get-pip.py
sudo -H python get-pip.py

# install skylines and the python dependencies

cd /vagrant
sudo -H pip install -r requirements.txt

# create PostGIS databases

sudo sudo -u postgres createuser -s vagrant

sudo sudo -u postgres createdb skylines -O vagrant
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines -c 'CREATE EXTENSION fuzzystrmatch;'

sudo sudo -u postgres createdb skylines_test -O vagrant
sudo sudo -u postgres psql -d skylines_test -c 'CREATE EXTENSION postgis;'
sudo sudo -u postgres psql -d skylines_test -c 'CREATE EXTENSION fuzzystrmatch;'

./manage.py db create

# build assets

./manage.py assets build

# compile translations

./manage.py babel compile

SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = 'ubuntu-12.04.2-x86_64'
  config.vm.box_url = 'http://puppet-vagrant-boxes.puppetlabs.com/ubuntu-server-12042-x64-vbox4210.box'

  config.vm.network 'forwarded_port', guest: 5000, host: 5000
  config.vm.network 'forwarded_port', guest: 5001, host: 5001

  config.vm.provision 'shell', inline: $script, privileged: false
end
