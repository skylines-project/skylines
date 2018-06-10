import { setupQunit } from '@pollyjs/core';

export function setupPolly(hooks, options = {}) {
  setupQunit(hooks, options);

  hooks.beforeEach(function() {
    let { server } = this.polly;

    server.get('/translations/:locale.json').passthrough();
  });
}
