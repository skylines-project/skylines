import Component from '@ember/component';
import { readOnly } from '@ember/object/computed';
import { or, and, not } from 'ember-awesome-macros';

export default Component.extend({
  classNames: ['form-group has-feedback'],
  classNameBindings: ['_showErrorClass:has-error', 'isValid:has-success'],

  validation: null,
  label: null,
  hasContent: true,
  forceErrorClass: false,
  didValidate: false,

  notValidating: not('validation.isValidating'),
  isValid: and('hasContent', 'validation.isValid', 'notValidating'),
  isInvalid: readOnly('validation.isInvalid'),
  showErrorClass: and('notValidating', 'showMessage', 'hasContent', 'validation'),
  showMessage: and(or('validation.isDirty', 'didValidate'), 'isInvalid'),
  _showErrorClass: or('showErrorClass', 'forceErrorClass'),
});
