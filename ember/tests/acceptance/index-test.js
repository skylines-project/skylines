import { describe, it, beforeEach, afterEach } from 'mocha';
import { expect } from 'chai';
import { visit, currentURL, find } from 'ember-native-dom-helpers';

import startApp from 'skylines/tests/helpers/start-app';
import destroyApp from 'skylines/tests/helpers/destroy-app';

describe('Acceptance | index', function() {
  let application;

  beforeEach(function() {
    application = startApp();
  });

  afterEach(function() {
    destroyApp(application);
  });

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
