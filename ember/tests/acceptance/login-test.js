import { describe, it } from 'mocha';
import { expect } from 'chai';
import { visit, click, find } from 'ember-native-dom-helpers';

import setupAcceptanceTest from 'skylines/tests/helpers/setup-acceptance-test';

describe('Acceptance | login', function() {
  setupAcceptanceTest(this);

  const LOGIN_DROPDOWN = '[data-test-login-dropdown]';
  const LOGIN_DROPDOWN_TOGGLE = `${LOGIN_DROPDOWN} a`;
  const LOGIN_EMAIL = '[data-test-input="login-email"]';

  it('login dropdown form stays visible when fields are focused', async function() {
    await visit('/');

    await click(LOGIN_DROPDOWN_TOGGLE);
    expect(find(LOGIN_DROPDOWN)).to.have.class('open');

    await click(LOGIN_EMAIL);
    expect(find(LOGIN_DROPDOWN)).to.have.class('open');
  });
});
