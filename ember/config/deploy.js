'use strict';

/* eslint-env node */

module.exports = function (deployTarget) {
  let ENV = {
    build: {},
    // include other plugin configuration that applies to all deploy targets here
    'revision-data': {
      type: 'git-commit',
    },
    compress: {
      keep: true,
      compression: ['gzip', 'brotli'],
    },
  };

  if (deployTarget === 'development') {
    ENV.build.environment = 'development';
    // configure other plugins for development deploy target here
  }

  if (deployTarget === 'staging') {
    ENV.build.environment = 'production';
    // configure other plugins for staging deploy target here
  }

  if (deployTarget === 'production') {
    ENV.build.environment = 'production';
    // configure other plugins for production deploy target here
    ENV['with-rsync'] = {
      host: 'skylines.aero',
      username: 'skylines',
      privateKeyPath: process.env['PRIVATE_KEY_PATH'],
      port: 2222,
      root: '/home/skylines/frontend',
      activationDestination() {
        return '/home/skylines/src/skylines/frontend/static';
      },
    };
  }

  // Note: if you need to build some configuration asynchronously, you can return
  // a promise that resolves with the ENV object instead of returning the
  // ENV object synchronously.
  return ENV;
};
