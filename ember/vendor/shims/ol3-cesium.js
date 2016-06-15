(function() {
  function vendorModule() {
    'use strict';

    return { 'default': self['olcs'] };
  }

  define('ol3-cesium', [], vendorModule);
})();
