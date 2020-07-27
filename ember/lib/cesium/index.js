'use strict';

const path = require('path');

const Funnel = require('broccoli-funnel');

module.exports = {
  name: 'cesium',

  isDevelopingAddon() {
    return true;
  },

  treeForPublic() {
    let cesiumPkgPath = require.resolve('cesium');
    let cesiumPath = path.dirname(cesiumPkgPath);
    let cesiumBuildPath = path.join(cesiumPath, 'Build', 'Cesium');
    return new Funnel(cesiumBuildPath, { destDir: 'cesium' });
  },
};
