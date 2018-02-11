import { helper } from '@ember/component/helper';

import pad from '../utils/pad';

export function formatHours([value]) {
  let h = Math.floor(value / 3600);
  let m = Math.floor((value % 3600) / 60);

  return `${h}:${pad(m)}`;
}

export default helper(formatHours);
