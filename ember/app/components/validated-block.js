import Ember from 'ember';

export default Ember.Component.extend({
  classNames: ['form-group has-feedback'],
  classNameBindings: ['showErrorClass:has-error', 'isValid:has-success'],

  validation: null,
  label: null,
  hasContent: true,

  notValidating: Ember.computed.not('validation.isValidating'),
  didValidate: Ember.computed.readOnly('targetObject.didValidate'),
  isValid: Ember.computed.and('hasContent', 'validation.isValid', 'notValidating'),
  isInvalid: Ember.computed.readOnly('validation.isInvalid'),
  showErrorClass: Ember.computed.and('notValidating', 'showMessage', 'hasContent', 'validation'),
  showMessage: Ember.computed('validation.isDirty', 'isInvalid', 'didValidate', function() {
    return (this.get('validation.isDirty') || this.get('didValidate')) && this.get('isInvalid');
  }),
});
