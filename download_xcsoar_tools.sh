#!/bin/bash
# Download XCsoar Tools script.

#  This script will attempt to download the binaries
#  required from XCsoar by Skylines to avoid
#  compiling XCsoar from source.

# Download XCsoar binaries with the -N flag,
# which will substitute the files when the server has
# a newer version, and add +x permissions.
wget -N --directory-prefix=bin http://download.xcsoar.org/skylines/bin/AnalyseFlight
chmod +x bin/AnalyseFlight

wget -N --directory-prefix=bin http://download.xcsoar.org/skylines/bin/FlightPath
chmod +x bin/FlightPath

