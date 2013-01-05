#!/bin/bash
#
# Prepare the SkyLines application and restart all daemons.  This is
# meant to be run on the production server.
#

set -e

cd `dirname $0`
python setup.py egg_info
python setup.py compile_catalog
python generate_assets.py
sv restart skylines-fastcgi
sv restart mapserver-fastcgi
sv restart skylines-daemon
