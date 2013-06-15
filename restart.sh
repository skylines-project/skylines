#!/bin/bash
#
# Prepare the SkyLines application and restart all daemons.  This is
# meant to be run on the production server.
#

set -e

cd `dirname $0`
python setup.py compile_catalog
python scripts/generate_assets.py
sv restart skylines-fastcgi
sv restart mapserver-fastcgi
sv restart skylines-daemon
sv restart celery-daemon
