import { helper } from '@ember/component/helper';

export function isUndefined([value]) {
  return value === undefined;
}

export default helper(isUndefined);
