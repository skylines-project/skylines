import Ember from 'ember';
import BaseValidator from 'ember-cp-validations/validators/base';

export default BaseValidator.extend({
  ajax: Ember.inject.service(),
  intl: Ember.inject.service(),

  validate(value, options, model) {
    if (!value) {
      return;
    }

    let name = value.trim();
    if (name === '') {
      return;
    }

    let data = { name };
    return this.get('ajax').request('/api/clubs', { data }).then(({ clubs }) => {
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
    });
  },
});
