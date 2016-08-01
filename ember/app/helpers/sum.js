import Ember from 'ember';

export function sum(numbers) {
  return numbers.reduce((a, b) => a + b, 0);
}

export default Ember.Helper.helper(sum);
