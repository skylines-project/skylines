import { setupQunit } from '@pollyjs/core';

export function setupPolly(hooks, options = {}) {
  setupQunit(hooks, options);

  hooks.beforeEach(function() {
    let { server } = this.polly;

    server.get('/_percy/:anything').passthrough();

    server.get('/translations/:locale.json').passthrough();

    server.get('/api/locale').intercept((req, res) => {
      res.status(200);
      res.json({ locale: 'en' });
    });
  });
}
