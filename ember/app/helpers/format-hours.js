/* globals pad */

import Ember from 'ember';

export function formatHours([value]) {
  let h = Math.floor(value / 3600);
  let m = Math.floor((value % 3600) / 60);

  return h + ':' + pad(m, 2);
}

export default Ember.Helper.helper(formatHours);
