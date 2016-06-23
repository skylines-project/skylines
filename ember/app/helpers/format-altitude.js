import Ember from 'ember';

import * as slUnits from '../utils/units';

export function formatAltitude([value]) {
  return slUnits.formatAltitude(value);
}

export default Ember.Helper.helper(formatAltitude);
