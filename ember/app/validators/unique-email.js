import Ember from 'ember';
import BaseValidator from 'ember-cp-validations/validators/base';

export default BaseValidator.extend({
  ajax: Ember.inject.service(),
  intl: Ember.inject.service(),
  account: Ember.inject.service(),

  validate(email, options) {
    if (!email) {
      return;
    }

    let json = { email };
    return this.get('ajax').request('/settings/email/check', { method: 'POST', json }).then(({ result }) => {
      return result ? true : this.get('intl').t(options.messageKey);
    });
  },
});
