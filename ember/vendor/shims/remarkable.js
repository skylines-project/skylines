(function() {
  function vendorModule() {
    'use strict';

    return { 'default': self['Remarkable'] };
  }

  define('remarkable', [], vendorModule);
})();
