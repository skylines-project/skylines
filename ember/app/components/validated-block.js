import Component from '@ember/component';
import { not, and, or, readOnly } from '@ember/object/computed';

export default class ValidatedBlock extends Component {
  tagName = '';

  validation = null;
  label = null;
  hasContent = true;
  forceErrorClass = false;
  didValidate = false;

  @not('validation.isValidating') notValidating;
  @and('hasContent', 'validation.isValid', 'notValidating') isValid;
  @readOnly('validation.isInvalid') isInvalid;
  @and('notValidating', 'showMessage', 'hasContent', 'validation') showErrorClass;
  @or('validation.isDirty', 'didValidate') _showMessage;
  @and('_showMessage', 'isInvalid') showMessage;
  @or('showErrorClass', 'forceErrorClass') _showErrorClass;
}
