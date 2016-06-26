import Ember from 'ember';
import BaseValidator from 'ember-cp-validations/validators/base';

export default BaseValidator.extend({
  ajax: Ember.inject.service(),
  intl: Ember.inject.service(),

  validate(password, options) {
    if (!password) {
      return;
    }

    let json = { password };
    return this.get('ajax').request('/settings/password/check', { method: 'POST', json }).then(({ result }) => {
      return result ? true : this.get('intl').t(options.messageKey);
    });
  },
});
