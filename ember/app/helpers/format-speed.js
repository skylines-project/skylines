import Ember from 'ember';

import * as slUnits from '../utils/units';

export function formatSpeed([value]) {
  return slUnits.formatSpeed(value);
}

export default Ember.Helper.helper(formatSpeed);
