CESIUM_BASE_URL = '/cesium/';

var CesiumSwitcher = function(opt_options) {
  var options = opt_options || {};
  var control = this;

  var enabled = false;
  var ol3d = undefined;

  var element = document.createElement('div');
  element.className = 'CesiumSwitcher ol-unselectable';

  var draw = function() {
    $(element).on('click touchend', $.proxy(onClick, control));
    control.setMode(this.enabled);
  };

  var onClick = function(evt) {
    control.setMode(!this.enabled);
    evt.preventDefault();
  };

  ol.control.Control.call(this, {
    element: element,
    target: options.target
  });

  draw();
};

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
  var _this = this;

  if (typeof Cesium === 'undefined') {
    var cesium = document.createElement('script');
    cesium.src = CESIUM_BASE_URL + 'Cesium.js';
    cesium.onload = function() {
      _this.enableCesium();
    };
    document.body.appendChild(cesium);
  }
};


/**
 * Enbables ol3-cesium.
 */
CesiumSwitcher.prototype.enableCesium = function() {
  if (!this.ol3d) {
    var map = this.getMap();

    this.ol3d = new olcs.OLCesium({map: map});
    var scene = this.ol3d.getCesiumScene();
    var terrainProvider = new Cesium.CesiumTerrainProvider({
      url: '//assets.agi.com/stk-terrain/world'
    });
    scene.terrainProvider = terrainProvider;
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
  var lonlat = ol.proj.transform([fix_data['lon'], fix_data['lat']],
                                 'EPSG:3857', 'EPSG:4326');

  var position = Cesium.Cartesian3.fromDegrees(lonlat[0], lonlat[1],
      fix_data['alt-msl'] + flight.getGeoid());
  var modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(position,
      fix_data['heading'] - Math.PI / 2, 0, 0);

  if (!flight.getPlane().entity) {
    var scene = this.ol3d.getCesiumScene();
    var entity = Cesium.Model.fromGltf({
      modelMatrix: modelMatrix,
      url: '../../images/Cesium_Air.gltf',
      scale: 1,
      minimumPixelSize: 64,
      allowPicking: false
    });
    scene.primitives.add(entity);
    flight.getPlane().entity = entity;
  } else {
    flight.getPlane().entity.modelMatrix = modelMatrix;
    flight.getPlane().entity.show = true;
  }
};


/**
 * @param {slFlight} flight
 */
CesiumSwitcher.prototype.hidePlane = function(flight) {
  if (flight.getPlane().entity) {
    flight.getPlane().entity.show = false;
  }
};
