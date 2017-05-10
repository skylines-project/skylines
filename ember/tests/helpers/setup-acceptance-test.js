/* eslint-disable mocha/no-top-level-hooks */

import { beforeEach, afterEach } from 'mocha';
import Pretender from 'pretender';

import startApp from 'skylines/tests/helpers/start-app';
import destroyApp from 'skylines/tests/helpers/destroy-app';

export default function setupAcceptanceTest() {
  beforeEach(function() {
    this.server = new Pretender(function() {
      this.get('/translations/:locale.json', this.passthrough);
    });

    this.application = startApp();
  });

  afterEach(function() {
    destroyApp(this.application);

    this.server.shutdown();
  });
}
