/* eslint-disable mocha/no-top-level-hooks */

import { beforeEach, afterEach } from 'mocha';

import startApp from 'skylines/tests/helpers/start-app';
import destroyApp from 'skylines/tests/helpers/destroy-app';

export default function setupAcceptanceTest() {
  beforeEach(function() {
    this.application = startApp();
  });

  afterEach(function() {
    destroyApp(this.application);
  });
}
