#!/usr/bin/env bash

set -e

OLCS_TAG=v1.36

## clone "ol-cesium" into "tmp" folder
if [ -d "/tmp/ol-cesium" ]; then
  (cd /tmp/ol-cesium && git fetch --all);
  (cd /tmp/ol-cesium && git checkout --force $OLCS_TAG);
  (cd /tmp/ol-cesium && git submodule update);
else
  git clone --branch=$OLCS_TAG --recursive https://github.com/openlayers/ol-cesium.git /tmp/ol-cesium;
fi

# copy custom build config into "ol-cesium" folder
cp -f config/ol-cesium.json /tmp/ol-cesium/build/olcesium.json

# build "ol-cesium" and "Cesium"
(cd /tmp/ol-cesium && make dist node_modules/@camptocamp/cesium/Build/Cesium/Cesium.js)

# copy "ol-cesium" to "vendor" folder
cp -f /tmp/ol-cesium/dist/olcesium.js vendor/openlayers/olcesium.js
cp -f /tmp/ol-cesium/node_modules/openlayers/css/ol.css vendor/openlayers/ol.css

# copy "Cesium" to "public" folder
rm -rf public/cesium
cp -r /tmp/ol-cesium/node_modules/@camptocamp/cesium/Build/Cesium public/cesium
