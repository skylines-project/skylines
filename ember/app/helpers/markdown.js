import { helper } from '@ember/component/helper';
import { htmlSafe } from '@ember/string';

import Remarkable from 'remarkable';

let remarkable = new Remarkable();

export function markdown([text]) {
  return htmlSafe(remarkable.render(text));
}

export default helper(markdown);
