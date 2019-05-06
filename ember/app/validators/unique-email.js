import { inject as service } from '@ember/service';

import BaseValidator from 'ember-cp-validations/validators/base';

export default BaseValidator.extend({
  ajax: service(),
  intl: service(),
  account: service(),

  async validate(email, options) {
    if (!email) {
      return;
    }

    let validResults = options.validResults || ['available', 'self'];

    let json = { email };
    let { result } = await this.ajax.request('/api/users/check-email', { method: 'POST', json });
    return validResults.indexOf(result) !== -1 ? true : this.intl.t(options.messageKey);
  },
});
