#!/usr/bin/env bash

OL3CS_TAG=v1.11

## clone "ol3-cesium" into "tmp" folder
if [ -d "tmp/ol3-cesium" ]; then
  (cd tmp/ol3-cesium && git fetch --all);
  (cd tmp/ol3-cesium && git checkout --force $OL3CS_TAG);
  (cd tmp/ol3-cesium && git submodule update);
else
  git clone --branch=$OL3CS_TAG --recursive https://github.com/openlayers/ol3-cesium.git tmp/ol3-cesium;
fi

# copy custom build config into "ol3-cesium" folder
cp -f config/ol3-cesium.json tmp/ol3-cesium/build/ol3cesium.json

# build "ol3-cesium" and "Cesium"
(cd tmp/ol3-cesium && make dist cesium/Build/Cesium/Cesium.js)

# copy "ol3-cesium" to "vendor" folder
cp -f tmp/ol3-cesium/dist/ol3cesium.js vendor/openlayers/ol3cesium.js
cp -f tmp/ol3-cesium/ol3/css/ol.css vendor/openlayers/ol.css

# copy "Cesium" to "public" folder
rm -rf public/cesium
cp -r tmp/ol3-cesium/cesium/Build/Cesium public/cesium
