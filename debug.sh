#!/bin/bash
#
# Prepares and launces the stand-alone debugging SkyLines server.
#

set -e

cd `dirname $0`

if test -z "$@"; then
    python generate_assets.py config/development.ini
    paster serve --reload config/development.ini
else
    python generate_assets.py "$@"
    paster serve --reload "$@"
fi
