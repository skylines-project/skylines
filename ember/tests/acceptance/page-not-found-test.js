import { expect } from 'chai';
import { describe, it, beforeEach } from 'mocha';
import { visit, currentURL, find } from 'ember-native-dom-helpers';

import setupAcceptanceTest from 'skylines/tests/helpers/setup-acceptance-test';

describe('Acceptance | page-not-found', function() {
  setupAcceptanceTest(this);

  describe('visiting /foobar', function() {
    beforeEach(async function() {
      await visit('/foobar');
    });

    it('will keep the URL at /foobar', function() {
      expect(currentURL()).to.equal('/foobar');
    });

    it('will show "Page not found" error message', function() {
      expect(find('.page-header').textContent).to.contain('Page not found');
    });
  });
});
