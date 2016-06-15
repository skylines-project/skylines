(function() {
  function vendorModule() {
    'use strict';

    return { 'default': self['ol'] };
  }

  define('openlayers', [], vendorModule);
})();
