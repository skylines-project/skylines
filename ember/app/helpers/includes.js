import Ember from 'ember';

export function includes([array, value]) {
  return array.includes(value);
}

export default Ember.Helper.helper(includes);
