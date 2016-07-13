/* global pad */

import Ember from 'ember';

export function formatSeconds([value]) {
  value %= 86400;
  let h = Math.floor(value / 3600);
  let m = Math.floor((value % 3600) / 60);
  let s = Math.floor(value % 3600 % 60);

  // Format the result into time strings
  return `${h}:${pad(m, 2)}:${pad(s, 2)}`;
}

export default Ember.Helper.helper(formatSeconds);
