import Ember from 'ember';
import BaseValidator from 'ember-cp-validations/validators/base';

export default BaseValidator.extend({
  ajax: Ember.inject.service(),
  intl: Ember.inject.service(),
  account: Ember.inject.service(),

  async validate(email, options) {
    if (!email) {
      return;
    }

    let validResults = options.validResults || ['available', 'self'];

    let json = { email };
    let { result } = await this.get('ajax').request('/api/users/check-email', { method: 'POST', json });
    return (validResults.indexOf(result) !== -1) ? true : this.get('intl').t(options.messageKey);
  },
});
