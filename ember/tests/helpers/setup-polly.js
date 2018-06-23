import { setupQunit } from '@pollyjs/core';

export function setupPolly(hooks, options = {}) {
  setupQunit(hooks, options);

  hooks.beforeEach(function() {
    let { server } = this.polly;

    server.any().on('request', req => {
      if (req.url.startsWith('/api')) {
        req.url = `https://skylines.aero${req.url}`;
      }
    });

    server.get('/_percy/:anything').passthrough();

    server.get('/translations/:locale.json').passthrough();

    server.get('/api/locale').intercept((req, res) => {
      res.status(200);
      res.json({ locale: 'en' });
    });
  });
}
