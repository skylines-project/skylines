import { visit, click } from '@ember/test-helpers';
import { module, test } from 'qunit';

import { setupApplicationTest } from '../test-helpers';

module('Acceptance | login', function (hooks) {
  setupApplicationTest(hooks);

  const LOGIN_DROPDOWN = '[data-test-login-dropdown]';
  const LOGIN_DROPDOWN_TOGGLE = `${LOGIN_DROPDOWN} a`;
  const LOGIN_EMAIL = '[data-test-input="login-email"]';

  test('login dropdown form stays visible when fields are focused', async function (assert) {
    await visit('/');

    await click(LOGIN_DROPDOWN_TOGGLE);
    assert.dom(LOGIN_DROPDOWN).hasClass('open');

    await click(LOGIN_EMAIL);
    assert.dom(LOGIN_DROPDOWN).hasClass('open');
  });
});
