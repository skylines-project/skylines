/* global slUnits */

import Ember from 'ember';

export function formatDistance([value]) {
  return slUnits.formatDistance(value);
}

export default Ember.Helper.helper(formatDistance);
