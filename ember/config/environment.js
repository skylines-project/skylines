module.exports = function(environment) {
  var ENV = {
    modulePrefix: 'skylines',
    environment: environment,
    rootURL: '/',
    locationType: 'auto',
    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. 'with-controller': true
      }
    },

    APP: {
      // Here you can pass flags/options to your application instance
      // when it is created
      rootElement: '#ember-application'
    },

    SKYLINES_TILE_BASEURL: 'https://skylines.aero/mapproxy',
  };

  if (environment === 'production') {
    ENV.BING_API_KEY = 'AqYIkJFKZXzNxVnZmmDyk52su5Le7GLfzshBTu_px5N1HYa6B2KW2qPemRltfc8g';
    ENV.MAPBOX_TILE_URL = 'https://a.tiles.mapbox.com/v4/skylines.l9bfkoko/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoic2t5bGluZXMiLCJhIjoiODR5cnAtcyJ9.OxutJHpnCaw6QQpxfl5ROA';
  }

  if (environment === 'development') {
    // ENV.APP.LOG_RESOLVER = true;
    // ENV.APP.LOG_ACTIVE_GENERATION = true;
    // ENV.APP.LOG_TRANSITIONS = true;
    // ENV.APP.LOG_TRANSITIONS_INTERNAL = true;
    // ENV.APP.LOG_VIEW_LOOKUPS = true;
  }

  if (environment === 'test') {
    // Testem prefers this...
    ENV.locationType = 'none';

    // keep test console output quieter
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.APP.rootElement = '#ember-testing';
  }

  if (environment === 'production') {

  }

  return ENV;
};
