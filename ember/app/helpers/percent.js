import Ember from 'ember';

export function percent([value, max]) {
  return Math.round(value * 100 / max);
}

export default Ember.Helper.helper(percent);
