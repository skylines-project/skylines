#!/bin/bash
#
# Prepare the SkyLines application and restart all daemons.  This is
# meant to be run on the production server.
#

set -e

cd `dirname $0`

# compile i18n .mo files
python setup.py compile_catalog

# generate JS/CSS assets
./manage.py assets build

# do database migrations
sudo -u skylines ./manage.py migrate upgrade

# restart services
sv restart skylines-fastcgi
sv restart mapserver-fastcgi
sv restart skylines-daemon
sv restart celery-daemon
