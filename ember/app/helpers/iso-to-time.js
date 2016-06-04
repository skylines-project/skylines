/* global moment */

import Ember from 'ember';

export function isoToTime([value]) {
  return moment.utc(value).format('HH:mm:ss');
}

export default Ember.Helper.helper(isoToTime);
