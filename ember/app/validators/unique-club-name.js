import Ember from 'ember';
import BaseValidator from 'ember-cp-validations/validators/base';

export default BaseValidator.extend({
  ajax: Ember.inject.service(),
  intl: Ember.inject.service(),

  async validate(value, options, model) {
    if (!value) {
      return;
    }

    let name = value.trim();
    if (name === '') {
      return;
    }

    let data = { name };
    let { clubs } = await this.get('ajax').request('/api/clubs', { data });
    if (clubs.length === 0) {
      return true;
    }

    if (options.idKey !== undefined) {
      let selfId = Ember.get(model, options.idKey);
      if (clubs[0].id === selfId) {
        return true;
      }
    }

    return this.get('intl').t(options.messageKey);
  },
});
