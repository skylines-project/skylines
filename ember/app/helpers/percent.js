import { helper } from '@ember/component/helper';

export function percent([value, max]) {
  return Math.round((value * 100) / max);
}

export default helper(percent);
