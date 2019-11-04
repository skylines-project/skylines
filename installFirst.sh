# After running these scripts in bash:
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
git clone https://github.com/hess8/skylinesC
cd skylinesC

sudo apt-get install -y --no-install-recommends \
    python python-dev 

sudo apt-get install -y --no-install-recommends \
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

pipenv install --dev
pipenv shell

#  Now run installNext.sh	
