import { inject as service } from '@ember/service';
import { isNone } from '@ember/utils';

import BaseValidator from 'ember-cp-validations/validators/base';

let NotEqualValidator = BaseValidator.extend({
  intl: service(),

  validate(value1, options, model) {
    let value2 = model.get(options.on);

    return isNone(value1) || isNone(value2) || value1 !== value2 ? true : this.intl.t(options.messageKey);
  },
});

NotEqualValidator.reopenClass({
  getDependentsFor(attribute, options) {
    return [`_model.${options.on}`];
  },
});

export default NotEqualValidator;
