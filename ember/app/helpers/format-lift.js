/* global slUnits */

import Ember from 'ember';

export function formatLift([value]) {
  return slUnits.formatLift(value);
}

export default Ember.Helper.helper(formatLift);
