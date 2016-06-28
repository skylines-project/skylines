import Ember from 'ember';

import * as slUnits from '../utils/units';

export function formatDistance([value], options) {
  return slUnits.formatDistance(value, options);
}

export default Ember.Helper.helper(formatDistance);
