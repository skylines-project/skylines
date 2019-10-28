import Component from '@ember/component';
import { readOnly, or, and, not } from '@ember/object/computed';

export default Component.extend({
  tagName: '',
  validation: null,
  label: null,
  hasContent: true,
  forceErrorClass: false,
  didValidate: false,

  notValidating: not('validation.isValidating'),
  isValid: and('hasContent', 'validation.isValid', 'notValidating'),
  isInvalid: readOnly('validation.isInvalid'),
  showErrorClass: and('notValidating', 'showMessage', 'hasContent', 'validation'),
  _showMessage: or('validation.isDirty', 'didValidate'),
  showMessage: and('_showMessage', 'isInvalid'),
  _showErrorClass: or('showErrorClass', 'forceErrorClass'),
});
