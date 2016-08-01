import Ember from 'ember';

import * as slUnits from '../utils/units';

export function formatAltitude([value], options) {
  return slUnits.formatAltitude(value, options);
}

export default Ember.Helper.helper(formatAltitude);
