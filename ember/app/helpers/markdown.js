import Ember from 'ember';
import Remarkable from 'remarkable';

let remarkable = new Remarkable();

export function markdown([text]) {
  return Ember.String.htmlSafe(remarkable.render(text));
}

export default Ember.Helper.helper(markdown);
