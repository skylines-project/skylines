import Ember from 'ember';

import { formatLift } from '../utils/units';

export default Ember.Helper.extend({
  compute([value], options) {
    return formatLift(value, options);
  },
});
