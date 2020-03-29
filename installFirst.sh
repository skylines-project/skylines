# First run this script.
#    sudo -u bret bash installFirst.sh
# Next run installLast.sh while in pipenv shell
#
# After sucessful installation:
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


#remove any locks
sudo killall apt apt-get
sudo rm /var/lib/apt/lists/lock
sudo rm /var/cache/apt/archives/lock
sudo rm /var/lib/dpkg/lock*
sudo dpkg --configure -a
sudo apt update

# sudo apt install -y git
sudo apt install -y curl
git clone https://github.com/hess8/skylinesC
cd skylinesC

# set environment variables

cat >> ~/.profile << EOF
export POSTGIS_GDAL_ENABLED_DRIVERS=GTiff
export POSTGIS_ENABLE_OUTDB_RASTERS=1
EOF

apt-get install -y python

# install pip
echo 'export PATH="${HOME}/.local/bin:$PATH"' >> ~/.bashrc
sudo apt install -y python-pip


# install pipenv
python -m pip install --user pipenv
# sudo -H pip install pipenv
# sudo chown $USER -R /home/$USER
pip install zipp

pipenv shell

echo 'Now run "sudo -u bret bash installLast.sh"'
