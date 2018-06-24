import { helper } from '@ember/component/helper';

export function truncate([text, length]) {
  return text.length <= length ? text : `${text.slice(0, length - 3)}...`;
}

export default helper(truncate);
