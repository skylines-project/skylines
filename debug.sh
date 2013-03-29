#!/bin/bash
#
# Prepares and launces the stand-alone debugging SkyLines server.
#

set -e

cd `dirname $0`

if test -z "$@"; then
    python generate_assets.py development.ini
    paster serve --reload development.ini
else
    python generate_assets.py "$@"
    paster serve --reload "$@"
fi
