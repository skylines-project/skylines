(function() {
  function vendorModule() {
    'use strict';

    return { 'default': self['olcs'] };
  }

  define('ol-cesium', [], vendorModule);
})();
