/* globals $, Cesium */

import ol from 'openlayers';
import olcs from 'ol3-cesium';

const CESIUM_BASE_URL = '/cesium/';

export default function CesiumSwitcher(opt_options) {
  let options = opt_options || {};

  this.enabled = false;
  this.ol3d = undefined;

  let element = document.createElement('div');
  element.className = 'CesiumSwitcher ol-unselectable';

  ol.control.Control.call(this, {
    element: element,
    target: options.target,
  });

  $(element).on('click touchend', evt => {
    this.setMode(!this.enabled);
    evt.preventDefault();
  });

  this.setMode(this.enabled);
}

ol.inherits(CesiumSwitcher, ol.control.Control);


/**
 * Sets the 3d mode.
 * @param {bool} mode - Enabled or not
 */
CesiumSwitcher.prototype.setMode = function(mode) {
  if (mode) {
    this.element.innerHTML = '<img src="../../images/2d.png"/>';
    $(this).triggerHandler('cesium_enable');
    this.loadCesium();
  } else {
    this.element.innerHTML = '<img src="../../images/3d.png"/>';
    if (this.ol3d) {
      $(this).triggerHandler('cesium_disable');
      this.ol3d.setEnabled(false);
      this.getMap().getView().setRotation(0);
    }
  }

  this.enabled = mode;
};


/**
 * Loads cesium.
 */
CesiumSwitcher.prototype.loadCesium = function() {
  if (typeof Cesium === 'undefined') {
    let cesium = document.createElement('script');
    cesium.src = CESIUM_BASE_URL + 'Cesium.js';
    cesium.onload = () => { this.enableCesium() };
    document.body.appendChild(cesium);
  }
};


/**
 * Enbables ol3-cesium.
 */
CesiumSwitcher.prototype.enableCesium = function() {
  if (!this.ol3d) {
    let map = this.getMap();

    this.ol3d = new olcs.OLCesium({map: map});
    let scene = this.ol3d.getCesiumScene();
    scene.terrainProvider = new Cesium.CesiumTerrainProvider({
      url: '//assets.agi.com/stk-terrain/world',
    });
    scene.globe.depthTestAgainstTerrain = true;
  }

  this.ol3d.setEnabled(true);
  this.ol3d.enableAutoRenderLoop();
};


/**
 * Returns the mode of cesium (3d or 2d).
 * @return {bool}
 */
CesiumSwitcher.prototype.getMode = function() {
  return this.enabled;
};

/**
 * @param {slFlight} flight
 * @param {Array} fix_data
 */
CesiumSwitcher.prototype.showPlane = function(flight, fix_data) {
  let lonlat = ol.proj.transform(fix_data.get('coordinate'), 'EPSG:3857', 'EPSG:4326');

  let position = Cesium.Cartesian3.fromDegrees(lonlat[0], lonlat[1],
      fix_data.get('alt-msl') + flight.get('geoid'));
  let modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(position,
      fix_data.get('heading') - Math.PI / 2, 0, 0);

  let entity = flight.get('entity');
  if (!entity) {
    let scene = this.ol3d.getCesiumScene();
    entity = Cesium.Model.fromGltf({
      modelMatrix: modelMatrix,
      url: '../../images/Cesium_Air.gltf',
      scale: 1,
      minimumPixelSize: 64,
      allowPicking: false,
    });
    scene.primitives.add(entity);
    flight.set('entity', entity);
  } else {
    entity.modelMatrix = modelMatrix;
    entity.show = true;
  }
};


/**
 * @param {slFlight} flight
 */
CesiumSwitcher.prototype.hidePlane = function(flight) {
  let entity = flight.get('entity');
  if (entity) {
    entity.show = false;
  }
};
