import Ember from 'ember';

import pad from '../utils/pad';

export function formatSeconds([value]) {
  value %= 86400;
  let h = Math.floor(value / 3600);
  let m = Math.floor((value % 3600) / 60);
  let s = Math.floor(value % 3600 % 60);

  // Format the result into time strings
  return `${h}:${pad(m)}:${pad(s)}`;
}

export default Ember.Helper.helper(formatSeconds);
