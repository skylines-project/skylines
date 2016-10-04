import Ember from 'ember';
import BaseValidator from 'ember-cp-validations/validators/base';

let NotEqualValidator = BaseValidator.extend({
  intl: Ember.inject.service(),

  validate(value1, options, model) {
    let value2 = model.get(options.on);

    return (Ember.isNone(value1) || Ember.isNone(value2) || value1 !== value2)
      ? true : this.get('intl').t(options.messageKey);
  },
});

NotEqualValidator.reopenClass({
  getDependentsFor(attribute, options) {
    return [`_model.${options.on}`];
  },
});

export default NotEqualValidator;
