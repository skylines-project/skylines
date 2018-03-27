import Pretender from 'pretender';

export function setupPretender(hooks) {
  hooks.beforeEach(function() {
    this.server = new Pretender(function() {
      this.get('/translations/:locale.json', this.passthrough);
    });
  });

  hooks.afterEach(function() {
    this.server.shutdown();
  });
}
