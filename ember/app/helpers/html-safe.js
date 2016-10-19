import Ember from 'ember';

export function htmlSafe([text]) {
  return Ember.String.htmlSafe(text);
}

export default Ember.Helper.helper(htmlSafe);
