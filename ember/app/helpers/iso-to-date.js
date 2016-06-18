import Ember from 'ember';

export function isoToDate([value]) {
  return new Date(value);
}

export default Ember.Helper.helper(isoToDate);
