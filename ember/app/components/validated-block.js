import Ember from 'ember';
import { or, and } from 'ember-awesome-macros';

export default Ember.Component.extend({
  classNames: ['form-group has-feedback'],
  classNameBindings: ['_showErrorClass:has-error', 'isValid:has-success'],

  validation: null,
  label: null,
  hasContent: true,
  forceErrorClass: false,

  notValidating: Ember.computed.not('validation.isValidating'),
  didValidate: Ember.computed.readOnly('targetObject.didValidate'),
  isValid: Ember.computed.and('hasContent', 'validation.isValid', 'notValidating'),
  isInvalid: Ember.computed.readOnly('validation.isInvalid'),
  showErrorClass: Ember.computed.and('notValidating', 'showMessage', 'hasContent', 'validation'),
  showMessage: and(or('validation.isDirty', 'didValidate'), 'isInvalid'),
  _showErrorClass: Ember.computed.or('showErrorClass', 'forceErrorClass'),
});
