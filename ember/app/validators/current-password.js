import Ember from 'ember';
import BaseValidator from 'ember-cp-validations/validators/base';

export default BaseValidator.extend({
  ajax: Ember.inject.service(),
  intl: Ember.inject.service(),

  async validate(password, options) {
    if (!password) {
      return;
    }

    let json = { password };
    let { result } = await this.get('ajax').request('/api/settings/password/check', { method: 'POST', json });
    return result ? true : this.get('intl').t(options.messageKey);
  },
});
