import { describe, it, beforeEach, afterEach } from 'mocha';
import { expect } from 'chai';
import { visit, currentURL } from 'ember-native-dom-helpers';

import startApp from 'skylines/tests/helpers/start-app';
import destroyApp from 'skylines/tests/helpers/destroy-app';

describe('Acceptance | flight upload', function() {
  let application;

  beforeEach(function() {
    application = startApp();
  });

  afterEach(function() {
    destroyApp(application);
  });

  describe('visiting /flights/upload (unauthenticated)', function() {
    beforeEach(async function() {
      await visit('/flights/upload');
    });

    it('redirects to the login page', function() {
      expect(currentURL()).to.equal('/login');
    });
  });
});
