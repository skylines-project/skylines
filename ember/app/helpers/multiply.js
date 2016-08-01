import Ember from 'ember';

export function multiply(numbers) {
  return numbers.reduce((a, b) => a * b, 1);
}

export default Ember.Helper.helper(multiply);
