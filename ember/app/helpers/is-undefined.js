import Ember from 'ember';

export function isUndefined([value]) {
  return value === undefined;
}

export default Ember.Helper.helper(isUndefined);
