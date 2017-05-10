import { describe, it, beforeEach } from 'mocha';
import { expect } from 'chai';
import { visit, currentURL, find } from 'ember-native-dom-helpers';

import setupAcceptanceTest from 'skylines/tests/helpers/setup-acceptance-test';

describe('Acceptance | index', function() {
  setupAcceptanceTest();

  describe('visiting /', function() {
    beforeEach(async function() {
      await visit('/');
      expect(currentURL()).to.equal('/');
    });

    it('shows a welcome message', function() {
      expect(find('[data-test-welcome-message]')).to.exist;
    });
  });
});
