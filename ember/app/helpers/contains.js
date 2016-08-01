import Ember from 'ember';

export function contains([array, value]) {
  return array.contains(value);
}

export default Ember.Helper.helper(contains);
