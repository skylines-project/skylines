import Ember from 'ember';

export function initials([name]) {
  let parts = name.split(/\s/);
  let initials = parts.filter(it => it.length > 2 && it.indexOf('.') === -1).map(it => it[0].toUpperCase());
  return initials.join('');
}

export default Ember.Helper.helper(initials);
