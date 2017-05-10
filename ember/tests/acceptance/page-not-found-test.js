import { expect } from 'chai';
import { describe, it, beforeEach, afterEach } from 'mocha';
import { visit } from 'ember-native-dom-helpers';

import startApp from '../helpers/start-app';
import destroyApp from '../helpers/destroy-app';

describe('Acceptance | page-not-found', function() {
  let application;

  beforeEach(function() {
    application = startApp();
  });

  afterEach(function() {
    destroyApp(application);
  });

  describe('visiting /foobar', function() {
    beforeEach(async function() {
      await visit('/foobar');
    });

    it('will keep the URL at /foobar', function() {
      expect(currentURL()).to.equal('/foobar');
    });

    it('will show "Page not found" error message', function() {
      expect(find('.page-header').text()).to.contain('Page not found');
    });
  });
});
