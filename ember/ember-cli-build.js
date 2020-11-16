'use strict';

/* eslint-env node */

let EmberApp = require('ember-cli/lib/broccoli/ember-app');

const CssModules = require('./build/css-modules');

const { USE_EMBROIDER } = process.env;

module.exports = function (defaults) {
  let environment = process.env.EMBER_ENV;
  let isProduction = environment === 'production';

  let pluginsToBlacklist = [];
  if (isProduction) {
    pluginsToBlacklist.push('ember-freestyle', 'freestyle');
  }

  let app = new EmberApp(defaults, {
    addons: {
      blacklist: pluginsToBlacklist,
    },

    cssModules: {
      extension: 'module.scss',
      intermediateOutputPath: USE_EMBROIDER ? '_css-modules.scss' : 'app/styles/_css-modules.scss',
      generateScopedName(className, modulePath) {
        return CssModules.generateName(className, modulePath, { isProduction });
      },
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

    sassOptions: { implementation: require('node-sass') },

    svgJar: {
      sourceDirs: ['public/svg'],
      optimizer: {
        plugins: [{ removeViewBox: false }],
      },
    },

    'ember-bootstrap': {
      bootstrapVersion: 3,
      importBootstrapFont: false,
      importBootstrapCSS: false,
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

  app.import('node_modules/ol/ol.css');

  app.import('bower_components/Flot/jquery.flot.js');
  app.import('bower_components/Flot/jquery.flot.time.js');
  app.import('bower_components/Flot/jquery.flot.crosshair.js');
  app.import('bower_components/Flot/jquery.flot.resize.js');
  app.import('bower_components/flot-marks/src/jquery.flot.marks.js');
  app.import('vendor/jquery.flot.flight-upload.js');

  // Monkey-patch the `findMissingKeys()` method
  let TranslationReducer = require('ember-intl/lib/broccoli/translation-reducer');
  TranslationReducer.prototype.findMissingKeys = function () {};

  if (USE_EMBROIDER) {
    const { Webpack } = require('@embroider/webpack');
    return require('@embroider/compat').compatBuild(app, Webpack);
  }

  return app.toTree();
};
