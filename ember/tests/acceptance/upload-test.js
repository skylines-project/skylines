import { describe, it, beforeEach } from 'mocha';
import { expect } from 'chai';
import { visit, currentURL } from 'ember-native-dom-helpers';

import setupAcceptanceTest from 'skylines/tests/helpers/setup-acceptance-test';

describe('Acceptance | flight upload', function() {
  setupAcceptanceTest(this);

  describe('visiting /flights/upload (unauthenticated)', function() {
    beforeEach(async function() {
      await visit('/flights/upload');
    });

    it('redirects to the login page', function() {
      expect(currentURL()).to.equal('/login');
    });
  });
});
