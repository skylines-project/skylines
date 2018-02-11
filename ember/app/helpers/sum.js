import { helper } from '@ember/component/helper';

export function sum(numbers) {
  return numbers.reduce((a, b) => a + b, 0);
}

export default helper(sum);
