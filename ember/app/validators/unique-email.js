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

    let validResults = options.validResults || ['available', 'self'];

    let json = { email };
    return this.get('ajax').request('/users/check-email', { method: 'POST', json })
      .then(({ result }) => ((validResults.indexOf(result) !== -1) ? true : this.get('intl').t(options.messageKey)));
  },
});
