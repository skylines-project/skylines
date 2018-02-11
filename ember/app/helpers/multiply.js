import { helper } from '@ember/component/helper';

export function multiply(numbers) {
  return numbers.reduce((a, b) => a * b, 1);
}

export default helper(multiply);
