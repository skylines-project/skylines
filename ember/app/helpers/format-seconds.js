/* global formatSecondsAsTime */

import Ember from 'ember';

export function formatSeconds([value]) {
  return formatSecondsAsTime(value);
}

export default Ember.Helper.helper(formatSeconds);
