'use strict';

/* eslint-env node */

module.exports = function(/* environment, appConfig */) {
  // See https://github.com/san650/ember-web-app#documentation for a list of
  // supported properties

  return {
    name: 'SkyLines',
    short_name: 'SkyLines',
    description: 'live tracking, flight database and competition framework',
    start_url: '/',
    display: 'standalone',
    background_color: '#fff',
    theme_color: '#222',
    icons: [
      {
        src: '/android-chrome-192x192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/android-chrome-512x512.png',
        sizes: '512x512',
        type: 'image/png',
      },
      {
        src: '/images/icons/apple-touch-icon.png',
        sizes: '180x180',
        type: 'image/png',
        targets: ['apple'],
      },
    ],
    apple: {
      statusBarStyle: 'black',
    },
  };
};
