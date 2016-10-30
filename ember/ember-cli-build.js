/* global require, module */
var EmberApp = require('ember-cli/lib/broccoli/ember-app');

module.exports = function(defaults) {
  var app = new EmberApp(defaults, {
    fingerprint: {
      extensions: ['css', 'js'],
      exclude: ['cesium'],
    },

    sourcemaps: {
      enabled: true,
      extensions: ['css', 'js'],
    },

    vendorFiles: {
      'jquery.js': 'bower_components/jquery/jquery.js',
    },
  });

  // Use `app.import` to add additional libraries to the generated
  // output files.
  //
  // If you need to use different assets in different
  // environments, specify an object as the first parameter. That
  // object's keys should be the environment name and the values
  // should be the asset to use in that environment.
  //
  // If the library that you are including contains AMD or ES6
  // modules that you would like to import into your application
  // please specify an object with the list of modules as keys
  // along with the exports of each module as its value.

  app.import('vendor/openlayers/ol3cesium.js');
  app.import('vendor/openlayers/ol.css');

  app.import('vendor/shims/openlayers.js');
  app.import('vendor/shims/ol3-cesium.js');

  app.import('bower_components/Flot/jquery.flot.js');
  app.import('bower_components/Flot/jquery.flot.time.js');
  app.import('bower_components/Flot/jquery.flot.crosshair.js');
  app.import('bower_components/Flot/jquery.flot.resize.js');
  app.import('bower_components/flot-marks/src/jquery.flot.marks.js');
  app.import('vendor/jquery.flot.flight-upload.js');

  app.import({
    development: 'bower_components/remarkable/dist/remarkable.js',
    production: 'bower_components/remarkable/dist/remarkable.min.js',
  });
  app.import('vendor/shims/remarkable.js');

  app.import({
    development: 'bower_components/BigScreen/bigscreen.js',
    production: 'bower_components/BigScreen/bigscreen.min.js',
  });

  app.import('vendor/bootstrap-datepicker/datepicker.js');
  app.import('vendor/bootstrap-datepicker/datepicker.css');

  app.import({
    development: 'bower_components/bootstrap/dist/js/bootstrap.js',
    production: 'bower_components/bootstrap/dist/js/bootstrap.min.js',
  });
  app.import({
    development: 'bower_components/bootstrap/dist/css/bootstrap.css',
    production: 'bower_components/bootstrap/dist/css/bootstrap.min.css',
  });
  app.import({
    development: 'bower_components/bootstrap/dist/css/bootstrap-theme.css',
    production: 'bower_components/bootstrap/dist/css/bootstrap-theme.min.css',
  });

  app.import({
    development: 'bower_components/moment/moment.js',
    production: 'bower_components/moment/min/moment.min.js',
  });

  app.import('bower_components/eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker.js');

  app.import({
    development: 'bower_components/sidebar-v2/js/jquery-sidebar.js',
    production: 'bower_components/sidebar-v2/js/jquery-sidebar.min.js',
  });

  // Monkey-patch the `findMissingKeys()` method
  var TranslationReducer = require('ember-intl/lib/broccoli/translation-reducer');
  TranslationReducer.prototype.findMissingKeys = function() {};

  return app.toTree();
};
