import { helper } from '@ember/component/helper';
import { htmlSafe as _htmlSafe } from '@ember/string';

export function htmlSafe([text]) {
  return _htmlSafe(text);
}

export default helper(htmlSafe);
