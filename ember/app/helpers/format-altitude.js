/* global slUnits */

import Ember from 'ember';

export function formatAltitude([value]) {
  return slUnits.formatAltitude(value);
}

export default Ember.Helper.helper(formatAltitude);
