import Ember from 'ember';

export function truncate([text, length]) {
  return (text.length <= length) ? text : `${text.slice(0, length - 3)}...`;

}

export default Ember.Helper.helper(truncate);
