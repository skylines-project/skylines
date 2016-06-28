import Ember from 'ember';

import * as slUnits from '../utils/units';

export function formatSpeed([value], options) {
  return slUnits.formatSpeed(value, options);
}

export default Ember.Helper.helper(formatSpeed);
