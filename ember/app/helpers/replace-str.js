import { helper } from '@ember/component/helper';

export function replaceSub([str, subStr, repStr]) {
  return str.replace(subStr,repStr);
}

export default helper(replaceSub);
