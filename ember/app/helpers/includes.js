import { helper } from '@ember/component/helper';

export function includes([array, value]) {
  return array.includes(value);
}

export default helper(includes);
