'use strict';

/* eslint-env node */

let EmberApp = require('ember-cli/lib/broccoli/ember-app');

module.exports = function(defaults) {
  let environment = process.env.EMBER_ENV;

  let pluginsToBlacklist = [];
  if (environment === 'production') {
    pluginsToBlacklist.push('ember-freestyle', 'freestyle');
  } else if (environment === 'test') {
    pluginsToBlacklist.push('ember-cli-pace');
  }

  let app = new EmberApp(defaults, {
    addons: {
      blacklist: pluginsToBlacklist,
    },

    fingerprint: {
      extensions: ['css', 'js'],
      exclude: ['cesium'],
    },

    'ember-cli-uglify': {
      exclude: ['cesium/**/*.js'],
    },

    sourcemaps: {
      enabled: true,
      extensions: ['css', 'js'],
    },

    vendorFiles: {
      'jquery.js': 'bower_components/jquery/jquery.js',
    },

    sassOptions: { implementation: require('node-sass') },

    svgJar: {
      sourceDirs: ['public/svg'],
      optimizer: {
        plugins: [{ removeViewBox: false }],
      },
    },

    'ember-bootstrap': {
      bootstrapVersion: 3,
      importBootstrapFont: true,
      importBootstrapCSS: false,
    },

    'ember-font-awesome': {
      includeStaticIcons: [
        'arrow-left',
        'arrow-right',
        'calendar',
        'chevron-down',
        'chevron-up',
        'clock-o',
        'facebook',
        'google-plus',
        'twitter',
      ],
    },

    freestyle: {
      snippetSearchPaths: ['lib/freestyle/app'],
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

  app.import('vendor/openlayers/olcesium.js');
  app.import('vendor/openlayers/ol.css');

  app.import('vendor/shims/openlayers.js');
  app.import('vendor/shims/ol-cesium.js');

  app.import('bower_components/Flot/jquery.flot.js');
  app.import('bower_components/Flot/jquery.flot.time.js');
  app.import('bower_components/Flot/jquery.flot.crosshair.js');
  app.import('bower_components/Flot/jquery.flot.resize.js');
  app.import('bower_components/flot-marks/src/jquery.flot.marks.js');
  app.import('vendor/jquery.flot.flight-upload.js');

  app.import({
    development: 'node_modules/bigscreen/bigscreen.js',
    production: 'node_modules/bigscreen/bigscreen.min.js',
  });

  app.import('vendor/bootstrap-datepicker/datepicker.js');
  app.import('vendor/bootstrap-datepicker/datepicker.css');

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
  let TranslationReducer = require('ember-intl/lib/broccoli/translation-reducer');
  TranslationReducer.prototype.findMissingKeys = function() {};

  return app.toTree();
};
