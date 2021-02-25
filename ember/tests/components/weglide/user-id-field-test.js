import { settled, fillIn, render, waitFor } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';
import { module, test } from 'qunit';

import { defer } from 'rsvp';

import { setupMirage } from 'ember-cli-mirage/test-support';
import { setupIntl, t } from 'ember-intl/test-support';

import { setupRenderingTest } from '../../test-helpers';

module('Component | Weglide::UserIdField', function (hooks) {
  setupRenderingTest(hooks);
  setupIntl(hooks);
  setupMirage(hooks);

  hooks.beforeEach(function (assert) {
    this.onChange = userId => assert.step(`change(${userId})`);
  });

  test('happy path', async function (assert) {
    let deferred = defer();
    this.server.get('https://api.weglide.org/v1/user/42', deferred.promise);

    await render(hbs`<Weglide::UserIdField @onChange={{this.onChange}} />`);
    assert.dom('[data-test-form-group]').doesNotHaveClass('has-error');
    assert.dom('[data-test-input]').hasValue('');
    assert
      .dom('[data-test-dynamic-help="settled"]')
      .hasText(`${t('weglide.example-prefix')} https://weglide.org/profile/123`);
    assert.dom('[data-test-name]').doesNotExist();
    assert.verifySteps([]);

    fillIn('[data-test-input]', '42');
    await waitFor('[data-test-dynamic-help="loading"]');
    assert.dom('[data-test-form-group]').doesNotHaveClass('has-error');
    assert.dom('[data-test-input]').hasValue('42');
    assert.dom('[data-test-dynamic-help="loading"]').hasText('https://weglide.org/profile/42');
    assert.dom('[data-test-name]').doesNotExist();
    assert.verifySteps(['change(42)']);

    deferred.resolve({ id: 42, name: 'John Doe' });
    await settled();
    assert.dom('[data-test-form-group]').doesNotHaveClass('has-error');
    assert.dom('[data-test-input]').hasValue('42');
    assert.dom('[data-test-dynamic-help="settled"]').hasText('https://weglide.org/profile/42 (John Doe)');
    assert.dom('[data-test-name]').hasText('(John Doe)');
    assert.verifySteps([]);
  });

  test('@initialValue sets the initial value', async function (assert) {
    this.server.get('https://api.weglide.org/v1/user/42', { id: 42, name: 'John Doe' });

    await render(hbs`<Weglide::UserIdField @initialValue="42" @onChange={{this.onChange}} />`);
    assert.dom('[data-test-form-group]').doesNotHaveClass('has-error');
    assert.dom('[data-test-input]').hasValue('42');
    assert.dom('[data-test-dynamic-help="settled"]').hasText('https://weglide.org/profile/42 (John Doe)');
    assert.dom('[data-test-name]').hasText('(John Doe)');
    assert.verifySteps([]);
  });

  test('error behavior', async function (assert) {
    this.server.get('https://api.weglide.org/v1/user/42', {}, 404);

    await render(hbs`<Weglide::UserIdField @onChange={{this.onChange}} />`);
    await fillIn('[data-test-input]', '42');
    assert.dom('[data-test-form-group]').doesNotHaveClass('has-error');
    assert.dom('[data-test-input]').hasValue('42');
    assert.dom('[data-test-dynamic-help="settled"]').hasText('https://weglide.org/profile/42');
    assert.dom('[data-test-name]').doesNotExist();
    assert.verifySteps(['change(42)']);
  });

  test('invalid values switch the field to error state', async function (assert) {
    await render(hbs`<Weglide::UserIdField @onChange={{this.onChange}} />`);
    await fillIn('[data-test-input]', 'a42');
    assert.dom('[data-test-form-group]').hasClass('has-error');
    assert.dom('[data-test-input]').hasValue('a42');
    assert
      .dom('[data-test-dynamic-help="settled"]')
      .hasText(`${t('weglide.example-prefix')} https://weglide.org/profile/123`);
    assert.dom('[data-test-name]').doesNotExist();
    assert.verifySteps(['change(null)']);
  });

  test('@disabled disables the input field', async function (assert) {
    this.set('disabled', false);
    await render(hbs`<Weglide::UserIdField @disabled={{this.disabled}} />`);
    assert.dom('[data-test-input]').isEnabled();

    this.set('disabled', true);
    await settled();
    assert.dom('[data-test-input]').isDisabled();
  });
});
