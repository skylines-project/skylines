#!/bin/bash
#
# Prepares and launces the stand-alone debugging SkyLines server.
#

set -e

cd `dirname $0`

if test -z "$@"; then
    python scripts/generate_assets.py config/development.ini
    paster serve --reload config/development.ini
else
    python scripts/generate_assets.py "$@"
    paster serve --reload "$@"
fi
