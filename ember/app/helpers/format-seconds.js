/* global formatSecondsAsTime */

import Ember from 'ember';

export function formatSeconds([value]) {
  value %= 86400;
  var h = Math.floor(value / 3600);
  var m = Math.floor((value % 3600) / 60);
  var s = Math.floor(value % 3600 % 60);

  // Format the result into time strings
  return pad(h, 2) + ':' + pad(m, 2) + ':' + pad(s, 2);
}

export default Ember.Helper.helper(formatSeconds);
