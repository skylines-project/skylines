import { get } from '@ember/object';
import { inject as service } from '@ember/service';

import BaseValidator from 'ember-cp-validations/validators/base';

export default BaseValidator.extend({
  ajax: service(),
  intl: service(),

  async validate(value, options, model) {
    if (!value) {
      return;
    }

    let name = value.trim();
    if (name === '') {
      return;
    }

    let data = { name };
    let { clubs } = await this.ajax.request('/api/clubs', { data });
    if (clubs.length === 0) {
      return true;
    }

    if (options.idKey !== undefined) {
      let selfId = get(model, options.idKey);
      if (clubs[0].id === selfId) {
        return true;
      }
    }

    return this.intl.t(options.messageKey);
  },
});
