import Ember from 'ember';

import * as slUnits from '../utils/units';

export function formatLift([value]) {
  return slUnits.formatLift(value);
}

export default Ember.Helper.helper(formatLift);
