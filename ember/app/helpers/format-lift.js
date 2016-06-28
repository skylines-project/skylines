import Ember from 'ember';

import * as slUnits from '../utils/units';

export function formatLift([value], options) {
  return slUnits.formatLift(value, options);
}

export default Ember.Helper.helper(formatLift);
