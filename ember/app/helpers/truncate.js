import Ember from 'ember';

export function truncate([text, length]) {
  if (text.length <= length)
    return text;

  return text.slice(0, length - 3) + '...';
}

export default Ember.Helper.helper(truncate);
