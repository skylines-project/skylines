import Ember from 'ember';

import { formatSpeed } from '../utils/units';

export default Ember.Helper.extend({
  compute([value], options) {
    return formatSpeed(value, options);
  },
});
