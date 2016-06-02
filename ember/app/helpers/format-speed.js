/* global slUnits */

import Ember from 'ember';

export function formatSpeed([value]) {
  return slUnits.formatSpeed(value);
}

export default Ember.Helper.helper(formatSpeed);
