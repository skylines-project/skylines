import Ember from 'ember';

import * as slUnits from '../utils/units';

export function formatDistance([value]) {
  return slUnits.formatDistance(value);
}

export default Ember.Helper.helper(formatDistance);
