# After running this script in bash:
# to run servers:
#     Backend
#       export FLASK_ENV=development
#       pipenv run ./manage.py runserver

#     Front end in separate terminal
#       you must be skylinesC/ember
#       sudo ember serve --proxy http://localhost:5000/
#       or
#       sudo DEBUG=\* ember serve  --proxy http://localhost:5000/

# To view website
#   http://localhost:4200/


#port forwarding needed between host and guest, from vagrant file
  # config.vm.network 'forwarded_port', guest: 5000, host: 5000
  # config.vm.network 'forwarded_port', guest: 5001, host: 5001
  # config.vm.network 'forwarded_port', guest: 5597, host: 5597, protocol: 'udp'


# sudo apt install -y git
# sudo apt install -y curl
git clone https://github.com/hess8/skylinesC
cd skylinesC

# set environment variables

cat >> ~/.profile << EOF
export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
export POSTGIS_ENABLE_OUTDB_RASTERS=1
EOF


# install pip

wget -N -nv https://bootstrap.pypa.io/get-pip.py
sudo -H python get-pip.py

# install pipenv

sudo -H pip install pipenv

pipenv shell