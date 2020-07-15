import { inject as service } from '@ember/service';

import BaseValidator from 'ember-cp-validations/validators/base';

export default class CurrentPassword extends BaseValidator {
  @service ajax;
  @service intl;

  async validate(password, options) {
    if (!password) {
      return;
    }

    let json = { password };
    let { result } = await this.ajax.request('/api/settings/password/check', { method: 'POST', json });
    return result ? true : this.intl.t(options.messageKey);
  }
}
